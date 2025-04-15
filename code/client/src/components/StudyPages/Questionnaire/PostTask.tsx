import BaseComponent from "../Base/Base";
import { useAppRoutes } from "../../../routes";
import { useEffect, useState } from "react";

export default function PostTask({ user_id }: { user_id: string }) {
  const [formUrl, setFromUrl] = useState<string>();
  const routes = useAppRoutes();

  useEffect(() => {
    const next_style = localStorage.getItem("taskStyle");
    const style = next_style === "considerate" ? "Involved" : "Considerate";
    const task_index = parseInt(localStorage.getItem("taskIndex") || "-1");
    setFromUrl(
      `https://docs.google.com/forms/d/e/1FAIpQLScfkasBZ7S7Dw1HfZKMmRRUExDjNFSpaaRaG6vVaB1nGioizg/viewform?usp=pp_url&entry.1506333392=${user_id}&entry.699152043=Task+${task_index}&entry.921395094=${style}&embedded=true`
    );
  }, []);

  const scrollToTop = () => {
    window.scrollTo(0, 0);
  };

  return (
    <BaseComponent
      pageTitle="Post-Task Questionnaire"
      buttonText="I have Submitted the Questionnaire"
      nextPath={routes.TASK}
    >
      {!!formUrl && (
        <iframe
          onLoad={scrollToTop}
          src={formUrl}
          style={{
            width: "640px",
            height: "2588px",
            border: "0",
          }}
          title="Google Form"
        />
      )}
    </BaseComponent>
  );
}
