export interface DashboardData {
  status: {
    level: string;
    color: string;
  };
  total_blocks: number;
  top_subnets: Array<{
    subnet: string;
    count: number;
  }>;
  top_ports: Record<string, number>;
  timeline_labels: string[];
  timeline_data: number[];
  ai_summary: string;
  tokens: {
    input: number;
    output: number;
  };
  error?: string;
}