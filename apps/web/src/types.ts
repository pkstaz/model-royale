export type Avatar = {
  id: string;
  name: string;
  slug: string;
  description: string;
  color: string;
  provider: string;
  base_url: string;
  model_id: string;
  has_api_key: boolean;
  temperature: number;
  max_tokens: number;
  personality: string;
  enabled: boolean;
  reachable: boolean;
};

export type EventInfo = {
  id: string;
  name: string;
  code: string;
  status: string;
  format: string;
  rounds_per_match: number;
  max_players: number;
  min_players: number;
  group_size: number;
  advance_per_group: number;
  reveal_mode: string;
  payoff: Record<string, number[]>;
  rules_prompt: string;
  judge_avatar_id?: string | null;
  invalid_move_policy: string;
  auto_advance: boolean;
};

export type Player = {
  id: string;
  event_id: string;
  display_name: string;
  avatar_id?: string | null;
  avatar?: Avatar | null;
  strategy_prompt: string;
  group_label?: string | null;
  eliminated: boolean;
  seed: number;
  locked: boolean;
};

export type Round = {
  id: string;
  index: number;
  move_a: string;
  move_b: string;
  points_a: number;
  points_b: number;
  rationale_a: string;
  rationale_b: string;
  judge_notes: string;
  invalid_a: boolean;
  invalid_b: boolean;
};

export type Match = {
  id: string;
  stage: string;
  wave: number;
  group_label?: string | null;
  bracket_slot: number;
  player_a_id?: string | null;
  player_b_id?: string | null;
  player_a_name?: string | null;
  player_b_name?: string | null;
  status: string;
  winner_id?: string | null;
  score_a: number;
  score_b: number;
  rounds: Round[];
};

export type Standing = {
  player_id: string;
  display_name: string;
  avatar?: string | null;
  avatar_color: string;
  group_label?: string | null;
  eliminated: boolean;
  points: number;
  wins: number;
  losses: number;
  matches: number;
  invalids: number;
  rank: number;
};

export type Live = {
  type?: string;
  event: EventInfo;
  players: Player[];
  matches: Match[];
  standings: Standing[];
};
