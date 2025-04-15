import {
  MDBModalDialog,
  MDBModalBody,
  MDBBtn,
  MDBModalContent,
  MDBModalFooter,
  MDBModal,
  MDBModalHeader,
  MDBModalTitle,
} from "mdb-react-ui-kit";

const Modal = ({
  modalOpen,
  closeModal,
  style,
}: {
  modalOpen: boolean;
  closeModal: () => void;
  style?: string;
}) => {
  return (
    <MDBModal open={modalOpen} onClose={closeModal} tabIndex="-1">
      <MDBModalDialog>
        <MDBModalContent>
          <MDBModalHeader>
            {/* <MDBModalTitle>{taskDetails.title}</MDBModalTitle> */}
            <MDBModalTitle>Tips and examples</MDBModalTitle>
            <MDBBtn
              className="btn-close"
              color="none"
              onClick={closeModal}
            ></MDBBtn>
          </MDBModalHeader>

          <MDBModalBody>
            {/* <p>{taskDetails.body}</p> */}
            <h3>Task Description</h3>
            <p>
              Your task is to identify and select{" "}
              <strong>5 research papers</strong> based on the provided research
              topic. Use the conversational recommender system to discover
              papers. <strong>Bookmark</strong> papers you find relevant.
            </p>
            <p>
              For this task{" "}
              {style === "optional" ? (
                <>
                  you can now switch between the two styles during conversation.{" "}
                  Click on the <strong>style switch button</strong> on top of
                  the chat window to change the style.
                </>
              ) : (
                <>
                  the agent uses <strong>{style}</strong> style.
                </>
              )}
            </p>
            <h3>Here are some examples of what you can ask:</h3>
            <ul>
              <li>
                <strong>Specify Preferences:</strong> You can specify topics of
                interest to get research paper recommendations. Note, that you
                can specify negative preference as well.
              </li>
              <li>
                <strong>Remove Preferences:</strong> You can remove previously
                stated preferences.
              </li>
              <li>
                <strong>Reset Preferences:</strong> You can reset all your
                preferences to start fresh.
              </li>
              <li>
                <strong>Request Preferences:</strong> You can ask for your
                current preferences.
              </li>
              <li>
                <strong>Ask for Topic Suggestions:</strong> You can ask the
                system to suggest topics based on your interests.
              </li>
              <li>
                <strong>Ask for Explanation:</strong> You can ask ADA to provide
                explanations about specific topics.
              </li>
            </ul>
          </MDBModalBody>

          <MDBModalFooter>
            <MDBBtn color="secondary" onClick={closeModal}>
              Close
            </MDBBtn>
          </MDBModalFooter>
        </MDBModalContent>
      </MDBModalDialog>
    </MDBModal>
  );
};

export default Modal;
