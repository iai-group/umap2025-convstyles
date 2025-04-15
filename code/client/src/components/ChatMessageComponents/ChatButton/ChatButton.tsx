import { MDBBtn } from "mdb-react-ui-kit";
import { Button } from "../../../contexts/socket/interfaces";

export default function ChatButton({
  button,
  onClick,
}: {
  button: Button;
  onClick: (button: Button) => void;
}): JSX.Element {
  const handleClick = () => {
    onClick(button);
  };

  return (
    <MDBBtn size="sm" className="btn-secondary" onClick={handleClick} rounded>
      {button.short_text}
    </MDBBtn>
  );
}
