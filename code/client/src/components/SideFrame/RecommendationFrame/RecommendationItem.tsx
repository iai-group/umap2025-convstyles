import {
  MDBCard,
  MDBCardBody,
  MDBCardText,
  MDBBtn,
  MDBCollapse,
} from "mdb-react-ui-kit";
import "./RecommendationItem.css";
import { Article } from "../../../contexts/socket/interfaces";
import { useEffect, useState } from "react";
import { useSocket } from "../../../contexts/socket/SocketContext";
import { useGlobalState } from "../../../contexts/GlobalStateContext";

declare global {
  interface Window {
    MathJax?: {
      typeset: () => Promise<void>;
      // Add other MathJax methods you might need here
    };
  }
}

const RecommendationItem = ({
  article,
  isBookmarked,
  toggleBookmarkClick,
}: {
  article: Article;
  isBookmarked: boolean;
  toggleBookmarkClick: () => void;
}) => {
  const { getExplanation, logEvent } = useSocket();
  const [showSummary, setShowSummary] = useState(false);
  const { globalState } = useGlobalState();

  const handleSummaryClick = () => {
    logEvent({
      event: showSummary ? "Collapse summary" : "Expand summary",
      metadata: { article_id: article.item_id },
    });
    setShowSummary(!showSummary);
  };

  const handleExplainClick = () => {
    logEvent({
      event: "Get recommendation explanation",
      metadata: { article_title: article.title, article_id: article.item_id },
    });
    if (globalState.chat_box.handleExplainRecommendation)
      globalState.chat_box.handleExplainRecommendation(article);
    getExplanation(article.item_id);
  };
  // const handlePositiveFeedback = () => {
  //   giveRecommendationFeedback(article_id, 1);
  // };
  // const handleNegativeFeedback = () => {
  //   giveRecommendationFeedback(article_id, -1);
  // };

  const convertLatexMathInline = (text: string) => {
    // Replace all occurrences of $$ with \( or \) depending on position (even or odd)
    return text.replace(/\$/g, (match, offset, string) => {
      // Count the number of $$ occurrences before the current match
      let precedingMatches = string.slice(0, offset).match(/\$/g);
      let count = precedingMatches ? precedingMatches.length : 0;

      // If count is even, replace with \(, otherwise replace with \)
      return count % 2 === 0 ? "\\(" : "\\)";
    });
  };

  useEffect(() => {
    window.MathJax?.typeset();
  }, []);

  return (
    <MDBCard
      className="recommendationCard"
      style={{
        border: "1px solid #ccc",
        marginBottom: "-1px",
        borderRadius: "0",
      }}
    >
      {/* <MDBCard className="mb-3 recommendationCard bg-light text-dark border-primary"> */}
      <MDBCardBody className="d-flex flex-column justify-content-between">
        <MDBCardText className="tex" style={{ fontSize: "15px" }}>
          {convertLatexMathInline(article.title)}
        </MDBCardText>
        {article.authors && (
          <MDBCardText style={{ fontSize: "12px" }}>
            {article.authors.join(", ")}
          </MDBCardText>
        )}
        <div className="d-flex justify-content-between">
          <a
            href="#"
            className="text-black text-decoration-underline me-auto"
            style={{ fontSize: "0.875rem" }}
            onClick={handleSummaryClick}
          >
            Abstract
          </a>
          <MDBBtn
            size="sm"
            className="btn-secondary me-2"
            style={{ width: "100px" }}
            onClick={handleExplainClick}
            disabled={globalState.chat_box.chatIsBusy}
          >
            Explain
          </MDBBtn>
          <MDBBtn
            // disabled={isBookmarked}
            size="sm"
            className={`me-2 ${isBookmarked ? "btn-danger" : "btn-secondary"}`}
            style={{ width: "100px" }}
            onClick={toggleBookmarkClick}
          >
            Bookmark
          </MDBBtn>
          {/* <MDBBtn
            size="sm"
            className="btn-secondary me-2"
            style={{ width: "122px" }}
            onClick={handlePositiveFeedback}
          >
            More like this
          </MDBBtn>
          <MDBBtn
            size="sm"
            className="btn-secondary"
            style={{ width: "122px" }}
            onClick={handleNegativeFeedback}
          >
            Less like this
          </MDBBtn> */}
        </div>
        <MDBCollapse open={showSummary}>
          <div className="mt-3">
            <div
              className="tex"
              style={{ fontSize: "14px" }}
              dangerouslySetInnerHTML={{
                __html: convertLatexMathInline(article.abstract),
              }}
            />
          </div>
        </MDBCollapse>
      </MDBCardBody>
    </MDBCard>
  );
};

export default RecommendationItem;
