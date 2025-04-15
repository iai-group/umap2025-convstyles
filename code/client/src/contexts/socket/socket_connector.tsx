import { useState, useEffect, useRef, useContext } from "react";
import io, { Socket } from "socket.io-client";
import { Settings } from "../../types";
import { SystemMessage, UserMessage, Article, Button } from "./interfaces";
import { ConfigContext, Mode } from "../ConfigContext";

const defaultSettings: Settings = {
  style: {
    name: "default",
    showStyleSwitch: false,
  },
};

export default function useSocketConnection() {
  const { config } = useContext(ConfigContext);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectError, setConnectError] = useState<Error | null>(null);
  const [settings, setSettings] = useState<Settings>();
  const onMessageRef = useRef<(message: SystemMessage) => void>();
  const onEOTRef = useRef<() => void>();
  const onOptionsRef = useRef<(options: Button[]) => void>();
  const onRecommendationsRef = useRef<(articles: Article[]) => void>();
  const onBookmarksRef = useRef<(articles: Article[]) => void>();
  const onPreferencesRef = useRef<(preference: string[]) => void>();
  // const onTaskDetailsRef = useRef<(TaskDetails: TaskDetails) => void>();
  const onRestartRef = useRef<() => void>();
  const onAuthenticationRef =
    useRef<(success: boolean, error: string) => void>();

  const mergeSettings = (incomingData?: Settings) => {
    if (!incomingData) {
      return defaultSettings;
    }

    return {
      ...defaultSettings,
      ...incomingData,
      style: {
        ...defaultSettings.style,
        ...incomingData.style,
      },
    };
  };

  useEffect(() => {
    if (!config.serverUrl) {
      console.error("Missing server url");
      return;
    }

    // console.log(config);
    const newSocket = io(config.serverUrl, {
      path: config.socketioPath,
    });
    setSocket(newSocket);

    newSocket.on("connect_error", (error) => {
      console.warn("Connection Error: ", error);
      setConnectError(error); // Set connection error
    });

    newSocket.on("connect_timeout", () => {
      console.error("Connection timeout");
      setConnectError(new Error("Connection timeout")); // Set timeout as connection error
    });

    newSocket.on("connect", () => {
      setIsConnected(true);
      setConnectError(null);
    });

    newSocket.on("disconnect", () => {
      setIsConnected(false);
    });

    newSocket.on("init", (settings?: Settings) => {
      const mergedSettings = mergeSettings(settings);
      setSettings(mergedSettings);
    });

    newSocket.on("message", (message: SystemMessage) => {
      // if (message.info) {
      //   console.log(message.info);
      // }
      onMessageRef.current && onMessageRef.current(message);
    });

    newSocket.on("EOT", () => {
      onEOTRef.current && onEOTRef.current();
    });

    newSocket.on("options", (options: Button[]) => {
      onOptionsRef.current && onOptionsRef.current(options);
    });

    newSocket.on("recommendations", (articles: Article[]) => {
      onRecommendationsRef.current && onRecommendationsRef.current(articles);
    });

    newSocket.on("bookmarks", (articles: Article[]) => {
      onBookmarksRef.current && onBookmarksRef.current(articles);
    });

    // TODO: Probably shouldnt be a list of strings. (Preference value?)
    newSocket.on("preferences", (preferences: string[]) => {
      onPreferencesRef.current && onPreferencesRef.current(preferences);
    });

    // newSocket.on("task_details", (taskDetails: TaskDetails) => {
    //   onTaskDetailsRef.current && onTaskDetailsRef.current(taskDetails);
    // });

    newSocket.on("restart", () => {
      onRestartRef.current && onRestartRef.current();
    });

    newSocket.on("authentication", ({ success, error }) => {
      onAuthenticationRef.current &&
        onAuthenticationRef.current(success, error);
    });

    return () => {
      newSocket.disconnect();
    };
  }, [config.serverUrl]);

  useEffect(() => {
    if (connectError) {
      // console.log(config);
      // TODO handle connection error
      console.error("Connection error", connectError);
    }
  }, [connectError]);

  const startConversation = () => {
    socket?.emit("start_conversation", {});
  };

  const sendMessage = (message: UserMessage) => {
    socket?.emit("message", message);
  };

  // const giveFeedback = (message: string, feedback: number) => {
  //   socket?.emit("feedback", { message: message, feedback: feedback });
  // };

  // const giveRecommendationFeedback = (item_id: string, feedback: number) => {
  //   socket?.emit("recommendation_feedback", {
  //     item_id: item_id,
  //     feedback: feedback,
  //   });
  // };
  const quickReply = (button: Button) => {
    socket?.emit("select_option", { option: button });
  };

  const bookmarkArticle = (item_id: string) => {
    socket?.emit("add_bookmark", { item_id: item_id });
  };

  const removeBookmarkedArticle = (item_id: string) => {
    socket?.emit("remove_bookmark", { item_id: item_id });
  };

  const removePreference = (topic: string) => {
    socket?.emit("remove_preference", { topic: topic });
  };

  const getBookmarks = () => {
    socket?.emit("get_bookmarks", {});
  };

  const getPreferences = () => {
    socket?.emit("get_preferences", {});
  };

  const getExplanation = (item_id: string) => {
    socket?.emit("get_explanation", { item_id: item_id });
  };

  // const getTaskDetails = () => {
  //   socket?.emit("get_task_details", {});
  // };

  const setStyle = (style: string) => {
    socket?.emit("set_style", { style: style });
  };

  const logEvent = (data?: {
    [key: string]: string | number | boolean | object;
  }) => {
    const to_log: Record<string, any> = {
      timestamp: new Date().toISOString(),
      page: window.location.pathname.split("/").pop(),
      ...window.localStorage,
      ...data,
    };
    socket?.emit("log_event", to_log);
  };

  const onMessage = (callback: (message: SystemMessage) => void) => {
    onMessageRef.current = callback;
  };

  const onEOT = (callback: () => void) => {
    onEOTRef.current = callback;
  };

  const onOptions = (callback: (options: Button[]) => void) => {
    onOptionsRef.current = callback;
  };

  const onPreferences = (callback: (topics: string[]) => void) => {
    onPreferencesRef.current = callback;
  };

  const onBookmarks = (callback: (articles: Article[]) => void) => {
    onBookmarksRef.current = callback;
  };

  // const onTaskDetails = (callback: (taskDetails: TaskDetails) => void) => {
  //   onTaskDetailsRef.current = callback;
  // };

  const onRecommendations = (callback: (articles: Article[]) => void) => {
    onRecommendationsRef.current = callback;
  };

  const onRestart = (callback: () => void) => {
    onRestartRef.current = callback;
  };

  const login = (username: string, password: string) => {
    socket?.emit("login", { username, password });
  };

  const register = (username: string, password: string) => {
    socket?.emit("register", { username, password });
  };

  const onAuthentication = (
    callback: (success: boolean, error: string) => void
  ) => {
    onAuthenticationRef.current = callback;
  };

  const reloadSocketConnection = () => {
    // console.log("Reloading socket connection");
    if (socket) {
      socket.disconnect();
      socket.connect();
    }
  };

  return {
    isConnected,
    settings,
    startConversation,
    sendMessage,
    // giveFeedback,
    // giveRecommendationFeedback,
    quickReply,
    bookmarkArticle,
    removeBookmarkedArticle,
    getBookmarks,
    onMessage,
    onEOT,
    onOptions,
    onBookmarks,
    onRecommendations,
    onRestart,
    removePreference,
    getPreferences,
    onPreferences,
    getExplanation,
    // getTaskDetails,
    // onTaskDetails,
    setStyle,
    logEvent,
    login,
    register,
    onAuthentication,
    reloadSocketConnection,
  };
}
