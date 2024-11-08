export interface Topic {
    title: string;
    tags: string[];
    difficulty?: string[];
}

export interface TopicList {
    topics: Topic[];
}