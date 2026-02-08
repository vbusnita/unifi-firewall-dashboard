from flask import Flask, render_template, jsonify, request, Response
from dotenv import load_dotenv
import os
import requests  # For Grok API in spoken report
import json
import websocket
import threading
from datetime import datetime

from .utils import fetch_firewall_drops, parse_firewall_drops, generate_ai_summary
from .ara_prompt import get_ara_voice_prompt

import pandas as pd
from datetime import datetime, timedelta
import random  # Only for fallback
import base64

import asyncio
import websockets

app = Flask(__name__)

def get_dashboard_data():
    try:
        print("Starting get_dashboard_data - attempting real Graylog fetch")

        # Feature 1: Fetch raw logs from Graylog
        raw_logs = fetch_firewall_drops(range_seconds=86400, limit=2000)  # 24h, generous limit
        print(f"Fetched {len(raw_logs)} raw logs from Graylog")

        if not raw_logs:
            raise ValueError("No logs returned from Graylog")

        # Feature 2: Parse into structured list + basic stats
        parsed_logs, parsed_stats = parse_firewall_drops(raw_logs)
        print(f"Parsed {len(parsed_logs)} valid drop events")

        if not parsed_logs:
            raise ValueError("No valid drops parsed from logs")

        total_blocks = parsed_stats['total_blocks']

        # Status logic
        if total_blocks < 50:
            status = {'level': 'Low Activity', 'color': '#00FF00'}
        elif total_blocks <= 300:
            status = {'level': 'Moderate Threats', 'color': '#FFFF00'}
        else:
            status = {'level': 'High Threat Level', 'color': '#FF0000'}
        print("Status calculated")

        # Use parsed stats directly where possible
        top_subnets = [
            {'subnet': subnet, 'count': count}
            for subnet, count in parsed_stats['top_src_subnets'].items()
        ]  # already sorted most_common(5)

        top_ports = parsed_stats['top_dst_ports']  # dict {port: count}

        # Timeline from real timestamps
        df = pd.DataFrame(parsed_logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)  # ensure UTC datetime
        # Convert to local timezone
        local_tz = datetime.now().astimezone().tzinfo
        df['timestamp'] = df['timestamp'].dt.tz_convert(local_tz)
        df['hour'] = df['timestamp'].dt.floor('h')

        min_time = df['timestamp'].min().floor('h')
        max_time = df['timestamp'].max().ceil('h')
        timeline_range = pd.date_range(min_time, max_time, freq='h')

        timeline = df.groupby('hour').size().reindex(timeline_range, fill_value=0).to_dict()
        timeline_labels = [dt.strftime('%H:%M') for dt in timeline.keys()]
        timeline_data = list(timeline.values())
        print("Timeline prepared from real data (local timezone)")

        # AI summary will be generated on demand
        ai_summary = "Click 'Generate AI Summary' to analyze current data."
        tokens = {'input': 0, 'output': 0}

        return {
            'status': status,
            'total_blocks': total_blocks,
            'top_subnets': top_subnets,
            'top_ports': top_ports,
            'timeline_labels': timeline_labels,
            'timeline_data': timeline_data,
            'ai_summary': ai_summary,
            'tokens': tokens,
            'error': None
        }

    except Exception as e:
        import traceback
        print("ERROR in get_dashboard_data:", str(e))
        print(traceback.format_exc())

        # Fallback to minimal error view
        return {
            'status': {'level': 'Error Loading Real Data', 'color': '#FF0000'},
            'total_blocks': 0,
            'top_subnets': [],
            'top_ports': {},
            'timeline_labels': [],
            'timeline_data': [],
            'ai_summary': f"Failed to load real data: {str(e)}. Check terminal logs, .env, Graylog connection.",
            'tokens': {'input': 0, 'output': 0},
            'error': str(e)
        }

@app.route('/')
def dashboard():
    data = get_dashboard_data()
    return render_template('index.html', data=data)

@app.route('/api/ai-summary', methods=['POST'])
def generate_ai_summary_endpoint():
    try:
        # Fetch current data
        raw_logs = fetch_firewall_drops(range_seconds=86400, limit=2000)
        parsed_logs, parsed_stats = parse_firewall_drops(raw_logs)

        if not parsed_logs:
            return jsonify({'error': 'No data available for analysis'})

        # Generate AI summary
        ai_result = generate_ai_summary(parsed_logs, use_normalizer=True, log_to_file=True)
        summary = ai_result['summary'] or "No summary generated."
        tokens = {
            'input': ai_result['input_tokens'],
            'output': ai_result['output_tokens']
        }

        return jsonify({
            'summary': summary,
            'tokens': tokens
        })
    except Exception as e:
        print(f"AI summary error: {e}")
        return jsonify({'error': str(e)})

async def ara_voice_handler(websocket):
    print("New Ara voice client connected")
    with open("ara_voice_log.txt", "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] New Ara voice client connected\n")

    # Only fetch the stats we need for voice — skip full AI summary to save tokens
    # (we can reuse dashboard logic but override/avoid the AI part)
    try:
        raw_logs = fetch_firewall_drops(range_seconds=86400, limit=2000)
        parsed_logs, parsed_stats = parse_firewall_drops(raw_logs)
        
        total_blocks = parsed_stats['total_blocks']
        
        if total_blocks < 50:
            status_level = 'Low Activity'
            status_color = '#00FF00'
        elif total_blocks <= 300:
            status_level = 'Moderate Threats'
            status_color = '#FFFF00'
        else:
            status_level = 'High Threat Level'
            status_color = '#FF0000'
        
        top_subnets = [
            {'subnet': subnet, 'count': count}
            for subnet, count in parsed_stats['top_src_subnets'].items()
        ]
        
        # Optional: add top ports if you want to mention in prompt
        top_ports = parsed_stats['top_dst_ports']
        
        data = {
            'status': {'level': status_level, 'color': status_color},
            'total_blocks': total_blocks,
            'top_subnets': top_subnets,
            'top_ports': top_ports,
            'ai_summary': "Voice briefing only — see dashboard for detailed AI summary."  # fallback
        }
    except Exception as e:
        print(f"Voice data fetch error: {e}")
        data = {
            'status': {'level': 'Error', 'color': '#FF0000'},
            'total_blocks': 0,
            'top_subnets': [],
            'top_ports': {},
            'ai_summary': f"Failed to load data: {str(e)}"
        }

    prompt = get_ara_voice_prompt(data)

    grok_key = os.getenv('GROK_API_KEY')
    if not grok_key:
        await websocket.send(json.dumps({'error': 'No GROK_API_KEY in .env'}))
        return

    with open("ara_voice_log.txt", "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Prompt: {prompt[:200]}...\n")

    try:
        async with websockets.connect(
            "wss://api.x.ai/v1/realtime",
            additional_headers={"Authorization": f"Bearer {grok_key}"}
        ) as xai_ws:
            print("Connected to xAI realtime")
            with open("ara_voice_log.txt", "a") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connected to xAI realtime\n")

            # Session update
            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "voice": "ara",
                    "turn_detection": {"type": "server_vad"},
                    "model": "grok-4-1-fast-reasoning",
                    "instructions": "Always respond with spoken audio. Use voice modality for all outputs."
                }
            }
            await xai_ws.send(json.dumps(session_update))
            print("Sent session.update to xAI")
            with open("ara_voice_log.txt", "a") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent session.update\n")

            # Create conversation item with prompt
            item_create = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}]
                }
            }
            await xai_ws.send(json.dumps(item_create))
            print("Sent conversation.item.create with prompt")
            with open("ara_voice_log.txt", "a") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent conversation.item.create\n")

            # Trigger response generation
            response_create = {"type": "response.create"}
            await xai_ws.send(json.dumps(response_create))
            print("Sent response.create — Ara should start speaking")
            with open("ara_voice_log.txt", "a") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sent response.create\n")

            async for msg in xai_ws:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if isinstance(msg, str):
                    print(f"xAI JSON: {msg[:200]}...")
                    with open("ara_voice_log.txt", "a") as f:
                        f.write(f"[{timestamp}] xAI JSON: {msg}\n")

                    try:
                        data = json.loads(msg)
                        if data.get('type') == 'response.output_audio.delta':
                            delta_b64 = data.get('delta', '')
                            if delta_b64:
                                audio_bytes = base64.b64decode(delta_b64)
                                print(f"xAI audio delta decoded ({len(audio_bytes)} bytes)")
                                await websocket.send(audio_bytes)  # Send as binary
                                with open("ara_voice_log.txt", "a") as f:
                                    f.write(f"[{timestamp}] xAI audio delta decoded ({len(audio_bytes)} bytes)\n")
                        else:
                            await websocket.send(msg)  # Forward non-audio JSON (e.g., transcripts, done)
                    except json.JSONDecodeError:
                        print("Invalid JSON from xAI")
                        await websocket.send(json.dumps({'error': 'Invalid JSON from xAI'}))
                elif isinstance(msg, bytes):
                    # Unlikely for xAI, but forward if happens
                    print(f"xAI raw binary ({len(msg)} bytes)")
                    await websocket.send(msg)
                    with open("ara_voice_log.txt", "a") as f:
                        f.write(f"[{timestamp}] xAI raw binary ({len(msg)} bytes)\n")

    except Exception as e:
        print(f"xAI error: {e}")
        with open("ara_voice_log.txt", "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {e}\n")
        await websocket.send(json.dumps({'error': str(e)}))
    finally:
        print("Ara voice client disconnected")
        with open("ara_voice_log.txt", "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ara voice client disconnected\n")

async def start_ara_voice_server():
    async with websockets.serve(ara_voice_handler, "0.0.0.0", 5002):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    # Clear log file
    open("ara_voice_log.txt", "w").close()

    # Start async WS server in a thread
    def run_ws_server():
        asyncio.run(start_ara_voice_server())

    ws_thread = threading.Thread(target=run_ws_server, daemon=True)
    ws_thread.start()

    # Start Flask with gevent
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    print("Starting Ara Voice WS server on ws://0.0.0.0:5002")
    print("Starting Flask HTTP server on http://127.0.0.1:5001")

    server = pywsgi.WSGIServer(
        ('0.0.0.0', 5001),
        app,
        handler_class=WebSocketHandler
    )
    server.serve_forever()