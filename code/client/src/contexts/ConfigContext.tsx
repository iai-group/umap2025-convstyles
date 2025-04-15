import React, { useState, ReactNode, useEffect } from "react";

export enum Mode {
  DEFAULT = "default",
  STYLE_TEST = "style_test",
  STUDY = "study",
}

export type Config = {
  name: string;
  serverUrl: string;
  useFeedback: boolean | false;
  useLogin: boolean | false;
  useRecommendationFrame: boolean | false;
  useWidget: boolean | false;
  socketioPath?: string | undefined;
  mode?: string;
  path: string;
};

type ConfigProviderProps = {
  children: ReactNode;
  user_defined_config?: Partial<Config>;
};

const defaultConfig: Config = {
  name: "Chatbot",
  serverUrl: "http://127.0.0.1:5000/",
  useFeedback: false,
  useLogin: false,
  useRecommendationFrame: false,
  useWidget: false,
  socketioPath: undefined,
  mode: Mode.DEFAULT,
  path: "/",
};

export const ConfigContext = React.createContext<{
  config: Config;
  setConfig: React.Dispatch<React.SetStateAction<Config>>;
}>({
  config: defaultConfig,
  setConfig: () => {},
});

export const ConfigProvider: React.FC<ConfigProviderProps> = ({
  children,
  user_defined_config,
}) => {
  const [config, setConfig] = useState<Config>(defaultConfig);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setConfig((prevConfig) => ({ ...prevConfig, ...user_defined_config }));
    setLoading(false);
  }, [user_defined_config, setConfig]);

  if (loading) {
    return <p>Loading configuration...</p>;
  }

  return (
    <ConfigContext.Provider value={{ config, setConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};
