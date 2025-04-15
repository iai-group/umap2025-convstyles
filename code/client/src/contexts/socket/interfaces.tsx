// TODO: Merge messages into a single ChatMessage
// export interface ChatMessage {
//   message: string;
//   metadata?: { [key: string]: any };
// }

export interface SystemMessage {
  intent: string;
  text: string;
  info?: string;
}

export interface UserMessage {
  message: string;
  metadata?: { [key: string]: any };
}

export interface Button {
  id: number;
  text: string;
  short_text: string;
}

export interface Article {
  item_id: string;
  title: string;
  abstract: string;
  authors: string[];
  score: number;
}
