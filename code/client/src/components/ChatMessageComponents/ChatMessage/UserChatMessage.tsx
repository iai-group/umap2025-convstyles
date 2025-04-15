import { MDBIcon } from "mdb-react-ui-kit";

export const UserChatMessage = ({
  message,
}: {
  message: string;
}): JSX.Element => {
  return (
    <div className="d-flex flex-row justify-content-end mb-1">
      <div
        className="p-2 ms-3 border"
        style={{ borderRadius: "15px", backgroundColor: "#fbfbfb" }}
      >
        <p className="small mb-0">{message}</p>
      </div>
      <div className="text-center ms-2">
        <MDBIcon fas size="2x" className="text-muted" icon="user-large" />
      </div>
      {/* <img
        src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava2-bg.webp"
        alt="User"
        style={{ width: "45px", height: "100%" }}
      /> */}
    </div>
  );
};
