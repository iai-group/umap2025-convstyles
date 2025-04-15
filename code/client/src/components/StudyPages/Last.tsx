import { useEffect } from "react";
import BaseComponent from "./Base/Base";

export default function Last() {
  useEffect(() => {
    localStorage.clear();
  });

  return (
    <BaseComponent pageTitle="Thank you!">
      <div style={{ marginTop: "10px" }}>
        <p>Thank you for participating in the study!</p>
      </div>
    </BaseComponent>
  );
}
