import { ConfigContext } from "../../contexts/ConfigContext";
import "./ChatEmbedded.css";
import { ReactNode, useContext } from "react";

import { MDBContainer, MDBRow, MDBCol } from "mdb-react-ui-kit";

import SideFrame from "../SideFrame/SideFrame";

export default function ChatEmbedded({
  children,
  task_index,
  task_set,
}: {
  children: ReactNode;
  task_index: number;
  task_set: number;
}) {
  const { config } = useContext(ConfigContext);

  if (config.useRecommendationFrame) {
    return (
      <MDBContainer>
        <MDBRow>
          <MDBCol md="6">{children}</MDBCol>
          <MDBCol md="6">
            <SideFrame task_index={task_index} task_set={task_set} />
          </MDBCol>
        </MDBRow>
      </MDBContainer>
    );
  } else {
    return <>{children}</>;
  }
}
