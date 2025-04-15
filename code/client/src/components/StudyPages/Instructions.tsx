import BaseComponent from "./Base/Base";
import { useAppRoutes } from "../../routes";

export default function Instructions() {
  const routes = useAppRoutes();
  return (
    <BaseComponent
      pageTitle="Instructions"
      buttonText="Next"
      nextPath={routes.INSTRUCTIONS_P2}
    >
      <div style={{ margin: "10px 50px" }}>
        <div className="task-description" style={{ marginBottom: "20px" }}>
          <h2>Tasks</h2>
          <p>
            In the following tasks, assume that you are a student and you are
            requested to find a set of <strong>5 research papers</strong> on a
            given research topic. These papers are expected to serve as a
            foundational resource on the specific topic for developing the
            ‘related work’ section of a research project that you are working
            on. Use the provided bookmark button to compile your selections. You
            can add and remove bookmarks without restrictions throughout the
            course of the task. Once satisfied with your selections, press{" "}
            <strong>Done</strong> in the top right corner of the page.
          </p>
        </div>

        <div className="topic-information">
          <h3>Resources provided in the tasks</h3>
          <p>You will be provided with:</p>
          <ul className="topic-info">
            <li>A topic title.</li>
            <li>A detailed topic description.</li>
          </ul>
          <p>
            Use this information to find relevant articles using the provided
            conversational agent.
          </p>
        </div>

        <div className="instructions" style={{ marginBottom: "10px" }}>
          <h3>Tasks guidelines</h3>
          <p>
            Follow these guidelines to effectively interact with the
            conversational assistant:
          </p>
          <ol className="instruction-detail" style={{ marginBottom: "20px" }}>
            <li>Interact with the agent using natural language.</li>
            <li>
              When stating preferences, focus on the relevant keywords to the
              topic. You may use both positive and negative preferences (E.g.,
              "I am interested in X" or "I don't care for Y").
            </li>
            <li>
              After you receive a list of recommendations, review them and
              refine your preferences to receive better-suited recommendations.
            </li>
            <li>
              At any point during the conversation, you can ask the system for
              your current preferences, topic suggestions or topic explanations.
            </li>
          </ol>
          {/* <p>
            Before moving on to the tasks you are welcome to test out the agent{" "}
            <strong>
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://gustav1.ux.uis.no/ada/test/"
              >
                here
              </a>
            </strong>
            . You can try to find some papers relevant to{" "}
            <strong>your research topic</strong>.
          </p> */}
        </div>
      </div>
    </BaseComponent>
  );
}
