import BaseComponent from "../Base/Base";
import { useAppRoutes } from "../../../routes";
import ChatEmbedded from "../../Embedded/ChatEmbedded";
import { ChatBox, StyleOption } from "../../ChatBox/ChatBox";
import { useEffect, useState } from "react";
// import Modal from "./Modal";
import { useSocket } from "../../../contexts/socket/SocketContext";
import Modal from "./Modal";

export default function Task({ style }: { style?: string | undefined }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [taskTopicSet, setTaskTopicSet] = useState<number>(0);
  const [taskIndex, setTaskIndex] = useState<number>(0);
  const [topicIndex, setTopicIndex] = useState<number>(0);
  const [taskStyle, setTaskStyle] = useState<string>();
  const { logEvent, reloadSocketConnection } = useSocket();
  // const [userReadInstructions, setUserReadInstructions] = useState(false);
  const routes = useAppRoutes();

  // useEffect(() => {
  //   reloadSocketConnection();
  // }, []);

  const shuffleArray = (array: number[]) => {
    return array.sort(() => Math.random() - 0.5);
  };

  useEffect(() => {
    // console.log("Task component mounted");
    // console.log("Task style: ", style);
    // reloadSocketConnection();
    const randomizedItems = JSON.parse(
      localStorage.getItem("randomizedItems") ||
        JSON.stringify(shuffleArray([0, 1, 2]))
    );
    const taskTopicSet = parseInt(
      localStorage.getItem("taskTopicSet") || (Math.random() < 0.5 ? "0" : "1")
    );
    const taskIndex = parseInt(localStorage.getItem("taskIndex") || "0");
    const topicIndex = randomizedItems[taskIndex];
    const taskStyle =
      style ||
      localStorage.getItem("taskStyle") ||
      (Math.random() < 0.5 ? "considerate" : "involved");
    // console.log("Task index: ", taskIndex);
    // console.log("Style: ", style);
    // console.log("taskStyle: ", taskStyle);

    setTaskTopicSet(taskTopicSet);
    setTaskIndex(taskIndex);
    setTopicIndex(topicIndex);
    setTaskStyle(taskStyle);

    localStorage.setItem("randomizedItems", JSON.stringify(randomizedItems));
    localStorage.setItem("taskTopicSet", taskTopicSet + "");
    localStorage.setItem("taskIndex", taskIndex + "");
    localStorage.setItem("topicIndex", topicIndex + "");
    localStorage.setItem("taskStyle", taskStyle + "");

    reloadSocketConnection();

    // NOTE: Shouldn't use dependencies in this useEffect
    // }, [reloadSocketConnection, style]);
  }, []);

  const taskCompleted = () => {
    logEvent({
      event: "Task completed",
    });
    localStorage.setItem("taskIndex", ((taskIndex + 1) % 3).toString());
    if (taskStyle === "involved")
      localStorage.setItem("taskStyle", "considerate");
    else localStorage.setItem("taskStyle", "involved");
  };

  const openModal = () => {
    logEvent({
      event: "Open hints",
    });
    setModalOpen(true);
  };
  const closeModal = () => {
    logEvent({
      event: "Close hints",
    });
    setModalOpen(false);
  };

  return (
    <BaseComponent
      pageTitle={`ArXivDigest Assistant (ADA) - Task ${taskIndex + 1}`}
      buttonText="Done"
      buttonHandler={taskCompleted}
      nextPath={taskIndex === 2 ? routes.POST_ALL_TASKS : routes.POST_TASK}
      openModal={openModal}
    >
      {/* {userReadInstructions && ( */}
      <ChatEmbedded task_index={topicIndex} task_set={taskTopicSet}>
        <ChatBox
          style={taskStyle as StyleOption}
          showStyleSwitch={taskIndex === 2}
        />
      </ChatEmbedded>
      {/* )} */}
      <Modal
        modalOpen={modalOpen}
        closeModal={closeModal}
        style={taskIndex === 2 ? "optional" : taskStyle}
      />
    </BaseComponent>
  );
}
