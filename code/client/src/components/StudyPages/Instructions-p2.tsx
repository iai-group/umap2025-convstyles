import BaseComponent from "./Base/Base";
import { useAppRoutes } from "../../routes";
import screenshot from "./Static/ui-mock-marked.png";

export default function InstructionsP2() {
  const routes = useAppRoutes();
  return (
    <BaseComponent
      pageTitle="Instructions"
      buttonText="Next"
      nextPath={routes.TASK}
    >
      <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
        <h2>UI and Navigation</h2>
        <p>Please refer to the annotated screenshot below:</p>

        <img
          src={screenshot}
          alt="UI Screenshot"
          style={{
            maxWidth: "70%",
            height: "auto",
            display: "block",
            margin: "0 auto 20px auto",
          }}
        />

        <p>
          The screenshot shows an example view of the task. It consists of 4
          main components:
        </p>
        <ol>
          <li>
            <strong>A:</strong> This component is used for the main navigation
            in the study.
          </li>
          <li>
            <strong>B:</strong> The main view of the chat interface.{" "}
            <strong>Note the conversational style switch in the header.</strong>{" "}
            In the first two tasks the switch is disabled, and in the last task
            you may use it to switch between the conversational styles.
          </li>
          <li>
            <strong>C:</strong> Navigation between the task components.
            <ol>
              <li>
                <strong>Research topic:</strong> The topic title and description
                for which to find the relevant papers.
              </li>
              <li>
                <strong>Recommendations:</strong> List of current
                recommendations.
              </li>
              <li>
                <strong>Bookmarks:</strong> List of bookmarked papers for the
                current task.
              </li>
            </ol>
          </li>
          <li>
            <strong>D:</strong> The view of the components from the previous
            point. Depends on the selected tab.
          </li>
        </ol>
      </div>
    </BaseComponent>
  );
}
