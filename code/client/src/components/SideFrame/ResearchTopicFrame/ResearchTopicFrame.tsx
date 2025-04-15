import { researchTopicsPhysics, researchTopicsML } from "./ResearchTopics";

const ResearchTopicFrame = ({
  topic_index,
  topic_set,
}: {
  topic_index: number;
  topic_set: number;
}) => {
  const researchTopic =
    topic_set == 1
      ? researchTopicsML[topic_index]
      : researchTopicsPhysics[topic_index];

  return (
    <div>
      <h3>{researchTopic.title}</h3>
      <p
        dangerouslySetInnerHTML={{
          __html: researchTopic.description_augmented,
        }}
      ></p>
    </div>
  );
};

export default ResearchTopicFrame;
