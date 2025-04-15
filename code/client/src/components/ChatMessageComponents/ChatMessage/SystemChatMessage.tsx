import { MDBIcon } from "mdb-react-ui-kit";
import { useEffect, useState } from "react";

export const SystemChatMessage = ({
  message,
}: {
  message: JSX.Element;
}): JSX.Element => {
  const [displayedMessage, setDisplayedMessage] = useState<JSX.Element>();

  useEffect(() => {
    setDisplayedMessage(message);
    // console.log(typeof message);
  }, [message]);

  return (
    <div className="d-flex flex-row justify-content-start mb-1">
      <div className="text-center">
        <MDBIcon fas size="2x" className="text-muted" icon="robot" />
        {/* {feedback && <Feedback message={message} on_feedback={feedback} />} */}
      </div>
      <div
        className="p-2 ms-3"
        style={{
          borderRadius: "15px",
          backgroundColor: "rgba(57, 192, 237, .2)",
        }}
      >
        {/* {!!image_url && (
          <div className="d-flex flex-row justify-content-center">
            <img
              src={image_url}
              alt=""
              style={{ width: "200px", height: "100%" }}
            />
          </div>
        )} */}
        <div className="small mb-0">{displayedMessage}</div>
      </div>
    </div>
  );
};
