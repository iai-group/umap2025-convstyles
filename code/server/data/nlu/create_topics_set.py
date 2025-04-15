from typing import Dict, List, Set

from ada.agent.nlu.annotators.joint_bert.train.dataset import (
    load_yaml,
    parse_example,
)

_ANNOTATED_EXAMPLES_PATH = "data/nlu/annotated_examples_v1.1.yaml"
_ANNOTATED_TOPICS_PATH = "data/nlu/topics.yaml"
_OLD_TOPICS_PATH = "data/nlu/topics.txt"


def parse_annotated_examples(path: str) -> Set[str]:
    """Parses the annotated examples to extract intent, text, and slot annotations.

    Args:
        examples: The examples to parse.

    Returns:
        The parsed examples.
    """
    topics = set()
    examples = load_yaml(path)
    for user_intent_set in examples.values():
        for system_intent_set in user_intent_set:
            for example in system_intent_set["user_utterances"]:
                clean_text, slot_annotations = parse_example(example)
                for topic, slot in slot_annotations:
                    topics.add(topic)
    return topics


def get_topics_from_yaml(path):
    topics = set()
    categorized_topics = load_yaml(path)
    for topic_list in categorized_topics.values():
        topics.update(topic_list)
    return topics


def update_topics(old_topics_path: str, new_topics: Set[str]):
    with open(old_topics_path, "r") as f:
        topics = set((topic.strip() for topic in f.read().splitlines()))
    topics.update(new_topics)
    with open(f"{old_topics_path}_updated", "w") as f:
        f.write("\n".join(topics))


if __name__ == "__main__":
    topics = set()
    topics.update(parse_annotated_examples(_ANNOTATED_EXAMPLES_PATH))
    topics.update(get_topics_from_yaml(_ANNOTATED_TOPICS_PATH))
    update_topics(_OLD_TOPICS_PATH, topics)
