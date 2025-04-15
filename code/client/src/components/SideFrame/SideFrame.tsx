import React, { useState, useCallback, useEffect } from "react";
import {
  MDBContainer,
  MDBTabs,
  MDBTabsItem,
  MDBTabsLink,
  MDBTabsContent,
  MDBTabsPane,
} from "mdb-react-ui-kit";
import ResearchTopicFrame from "./ResearchTopicFrame/ResearchTopicFrame";
import { useSocket } from "../../contexts/socket/SocketContext";
import { Article } from "../../contexts/socket/interfaces";
import RecommendationItem from "./RecommendationFrame/RecommendationItem";
import BookmarkItem from "./BookmarkFrame/BookmarkItem";
// import UserPreferences from "./UserItems/PreferencesFrame";

type SideFrameProps = {
  task_index: number;
  task_set: number;
};

const SideFrame: React.FC<SideFrameProps> = ({ task_index, task_set }) => {
  const {
    onRecommendations,
    bookmarkArticle,
    logEvent,
    getBookmarks,
    onBookmarks,
    removeBookmarkedArticle,
  } = useSocket();
  const [activeTab, setActiveTab] = useState("RT");
  const [bookmarkState, setBookmarkState] = useState<Article[]>([]);
  const [recommendationsState, setRecommendationsState] = useState<Article[]>(
    []
  );

  useEffect(() => {
    getBookmarks();
  }, [getBookmarks]);

  const toggleTab = useCallback(
    (tab: string) => {
      logEvent({
        event: "Tab change",
        metadata: { tab: tab },
      });
      if (activeTab !== tab) setActiveTab(tab);
    },
    [activeTab, logEvent]
  );

  useEffect(() => {
    onRecommendations((articles: Article[]) => {
      // console.log(articles);
      setRecommendationsState(articles);
      toggleTab("recommendation");
    });
  }, [onRecommendations, toggleTab]);

  useEffect(() => {
    onBookmarks((articles: Article[]) => setBookmarkState(articles));
  }, [onBookmarks]);

  const checkIsBookmarked = (article_id: string) => {
    return bookmarkState.some((item) => item.item_id === article_id);
  };

  const toggleBookmarkClick = (article_id: string) => {
    if (checkIsBookmarked(article_id)) {
      handleRemoveBookmaredkArticle(article_id);
    } else {
      handleBookmarkClick(article_id);
    }
  };

  const handleBookmarkClick = (article_id: string) => {
    if (checkIsBookmarked(article_id)) return;
    const article = recommendationsState.find(
      (item) => item.item_id === article_id
    );
    if (!article) {
      logEvent({
        event: "Error",
        metadata: { article_id: article_id, error: "Article not found" },
      });
      return;
    }
    logEvent({
      event: "Bookmark article",
      metadata: { article_id: article_id },
    });
    bookmarkArticle(article.item_id);
    setBookmarkState((prev) => [...prev, article]);
  };

  const handleRemoveBookmaredkArticle = (article_id: string) => {
    if (!checkIsBookmarked(article_id)) return;
    logEvent({
      event: "Remove bookmarked article",
      metadata: { article_id: article_id },
    });
    removeBookmarkedArticle(article_id);
    setBookmarkState((prev) =>
      prev.filter((item) => item.item_id !== article_id)
    );
  };

  return (
    <MDBContainer>
      <MDBTabs className="mb-2">
        <MDBTabsItem>
          <MDBTabsLink
            onClick={() => toggleTab("RT")}
            active={activeTab === "RT"}
          >
            Research Topic
          </MDBTabsLink>
        </MDBTabsItem>
        <MDBTabsItem>
          <MDBTabsLink
            onClick={() => toggleTab("recommendation")}
            active={activeTab === "recommendation"}
          >
            Recommendations
          </MDBTabsLink>
        </MDBTabsItem>
        <MDBTabsItem>
          <MDBTabsLink
            onClick={() => toggleTab("bookmarks")}
            active={activeTab === "bookmarks"}
          >
            Bookmarks
          </MDBTabsLink>
        </MDBTabsItem>
        {/* <MDBTabsItem>
          <MDBTabsLink
            onClick={() => toggleTab("preferences")}
            active={activeTab === "preferences"}
          >
            My Preferences
          </MDBTabsLink>
        </MDBTabsItem> */}
      </MDBTabs>
      <MDBTabsContent>
        <MDBTabsPane open={activeTab === "RT"}>
          <ResearchTopicFrame topic_index={task_index} topic_set={task_set} />
        </MDBTabsPane>
        <MDBTabsPane open={activeTab === "recommendation"}>
          <div
            style={{
              paddingBottom: "5px",
              maxHeight: "max(600px, calc(100vh - 200px))",
              overflowY: "auto",
            }}
          >
            {recommendationsState.map((article, index) => (
              <RecommendationItem
                key={article.item_id + "test"}
                article={article}
                isBookmarked={checkIsBookmarked(article.item_id)}
                toggleBookmarkClick={() => toggleBookmarkClick(article.item_id)}
              />
            ))}
          </div>
        </MDBTabsPane>
        <MDBTabsPane open={activeTab === "bookmarks"}>
          <MDBContainer>
            <div
              style={{
                maxHeight: "max(600px, calc(100vh - 200px))",
                overflowY: "auto",
              }}
            >
              {bookmarkState.map((article, index) => (
                <BookmarkItem
                  key={article.item_id}
                  article_id={article.item_id}
                  title={article.title}
                  authors={article.authors}
                  handleRemoveBookmaredkArticle={handleRemoveBookmaredkArticle}
                />
              ))}
            </div>
          </MDBContainer>
        </MDBTabsPane>
        {/* <MDBTabsPane open={activeTab === "preferences"}>
          <UserPreferences isActive={activeTab === "preferences"} />
        </MDBTabsPane> */}
      </MDBTabsContent>
    </MDBContainer>
  );
};

export default SideFrame;
