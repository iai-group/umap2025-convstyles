import { useCallback, useContext, useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { ConfigContext } from "./contexts/ConfigContext";
import Welcome from "./components/StudyPages/Welcome";
import PreTask from "./components/StudyPages/Questionnaire/PreTask";
import Instructions from "./components/StudyPages/Instructions";
import InstructionsP2 from "./components/StudyPages/Instructions-p2";
import PostTask from "./components/StudyPages/Questionnaire/PostTask";
import PostAllTasks from "./components/StudyPages/Questionnaire/PostAllTasks";
import Last from "./components/StudyPages/Last";
import { useAppRoutes } from "./routes";
import Task from "./components/StudyPages/Task/Task";
import { useSocket } from "./contexts/socket/SocketContext";

export enum StyleOption {
  DEFAULT = "default",
  CONSIDERATE = "considerate",
  INVOLVED = "involved",
}

export default function App() {
  const { config } = useContext(ConfigContext);
  const { logEvent } = useSocket();
  const [userId, setUserId] = useState<string>("");
  const routes = useAppRoutes();

  const generateToken = () => {
    const token =
      Date.now().toString(36) + Math.random().toString(36).substring(2);
    const expirationTime = new Date().getTime() + 24 * 60 * 60 * 1000;
    localStorage.setItem(
      "userStudyID",
      JSON.stringify({ userid: token, expiresAt: expirationTime })
    );
    return token;
  };

  const getUserStudyID = useCallback(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const userIdFromUrl = urlParams.get("userid");

    if (userIdFromUrl) {
      // Store the user ID from the URL in localStorage
      const tokenData = {
        userid: userIdFromUrl,
        expiresAt: new Date().getTime() + 7 * 24 * 60 * 60 * 1000, // 24 hours expiry, adjust as needed
      };
      localStorage.setItem("userStudyID", JSON.stringify(tokenData));
      return userIdFromUrl;
    }

    const storedItem = localStorage.getItem("userStudyID");
    if (storedItem) {
      const { userid, expiresAt } = JSON.parse(storedItem);
      if (new Date().getTime() <= expiresAt) {
        return userid;
      }
    }

    localStorage.clear();
    return generateToken();
  }, []);

  useEffect(() => {
    const user_id = getUserStudyID();
    console.log("user_id", user_id);
    setUserId(user_id);
    logEvent({ event: "App start" });
  }, [logEvent, getUserStudyID]);

  // useEffect(() => {
  //   console.log("config", config);
  // }, [config]);

  if (!userId) {
    return <div>Loading...</div>;
  }

  return (
    <Router basename={config.path}>
      <Routes>
        <Route path={routes.HOME} element={<Welcome />} />
        <Route path={routes.INSTRUCTIONS} element={<Instructions />} />
        <Route path={routes.INSTRUCTIONS_P2} element={<InstructionsP2 />} />
        <Route path={routes.PRE_TASK} element={<PreTask user_id={userId} />} />
        <Route path={routes.TASK} element={<Task />} />
        <Route
          path={routes.INVOLVED}
          element={<Task style={StyleOption.INVOLVED} />}
        />
        <Route
          path={routes.CONSIDERATE}
          element={<Task style={StyleOption.CONSIDERATE} />}
        />
        <Route
          path={routes.DEFAULT}
          element={<Task style={StyleOption.DEFAULT} />}
        />
        <Route
          path={routes.POST_TASK}
          element={<PostTask user_id={userId} />}
        />
        <Route
          path={routes.POST_ALL_TASKS}
          element={<PostAllTasks user_id={userId} />}
        />
        <Route path={routes.LAST} element={<Last />} />
      </Routes>
    </Router>
  );
}

//   const content = config.useLogin && !user ? <LoginForm /> : <ChatBox />;
//   return config.useWidget ? (
//     <ChatWidget>{content}</ChatWidget>
//   ) : (
//     <ChatEmbedded>{content}</ChatEmbedded>
//   );
// }
