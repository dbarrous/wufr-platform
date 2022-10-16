import React from "react";
import { useState, useEffect } from "react";
import {
  Layout,
  Input,
  AutoComplete,
  Button,
  Card,
  Modal,
  Checkbox,
  Radio,
} from "antd";
import styled from "styled-components";
import { DeleteOutlined } from "@ant-design/icons";
// import react router link
import { Link } from "react-router-dom";
const { Option } = AutoComplete;

const AppLayout = styled(Layout)`
  min-height: 100%;

  .app-header {
    background-color: #080c11;
    padding: 0 24px;
  }

  .login-button {
    color: white;
    font-size: 1.5rem;
    width: 50%;
    height: 4rem;
    margin: 2rem auto;
    line-height: 1;
    background-color: #3cb989;
    padding: 1rem;
    &:hover {
      opacity: 90%;
    }
  }
`;
// Styled controlled Input
const StyledInput = styled(Input)`
  width: 50%;
  margin: auto;
  margin-top: 1rem;
`;
const ContentLayout = styled(Layout)`
  border-top-left-radius: ${(props) => (props.showBorder ? "10px" : "none")};
  background: #f3f8fc;
  display: flex;

  width: 100%;
`;

const LoginContainer = styled.div`
  margin: auto;
  margin-top: 5em;
  color: #b0b0b0;
  display: flex;
  flex-wrap: wrap;
`;

const StyledHeader = styled.h1`
  color: #05b6ec;
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
`;

const StyledSubText = styled.p`
  width: 70%;
  color: #b0b0b0;
  font-size: 1.5rem;
  text-align: center;
  margin: auto;
  margin-top: 1rem;
`;

const StyledSearchBarContainer = styled.div`
  width: 40vw;
  height: 5rem;
  padding: 0 1rem;
  margin: auto;
  margin-top: 1rem;
`;

const MediaPage = (props) => {
  const {
    isAuthenticated,
    isLoading,
    loginWithRedirect,
    wufrUser,
    user,
    mediaType,
    getAccessTokenSilently,
  } = props;

  //Pop id off of the url
  let id =
    window.location.href.split("/")[window.location.href.split("/").length - 1];

  const [value, setValue] = useState("");
  const [options, setOptions] = useState([]);
  const [media, setMedia] = useState([]);
  const [media2, setMedia2] = useState([]);
  const [media3, setMedia3] = useState([]);
  const [reviews, setReviews] = useState(null);
  const [score, setScore] = useState(null);
  const [external_media, setExternalMedia] = useState(null);
  const [external_media2, setExternalMedia2] = useState(null);

  const [averageScore, setAverageScore] = useState(null);
  // State for the form
  const [formState, setFormState] = useState({
    title: "",
    description: "",
    score: 0,
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const showModal = () => {
    setIsModalOpen(true);
  };
  const handleOk = () => {
    handleCreateReview();
    setIsModalOpen(false);
  };
  const handleCancel = () => {
    setIsModalOpen(false);
  };
  // Find 640 image in array of images
  const find640 = (images) => {
    let image = images.find((image) => image.width === 640);
    return image.url;
  };
  //effect run once on page load
  useEffect(() => {
    const loadMedia = async (id, mediaType) => {
      try {
        const token = await getAccessTokenSilently();
        const response = await fetch(
          `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/search?${mediaType}_id='${id}'`,
          {
            mode: "cors",
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Access-Control-Allow-Origin": "*", // Required for CORS support to work
              "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
            },
          }
        );
        const responseData = await response.json();
        setMedia(JSON.parse(responseData.body));
        if (mediaType === "song") {
          const response = await fetch(
            `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/search?artists_for_song_id='${id}'`,
            {
              mode: "cors",
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`,
                "Access-Control-Allow-Origin": "*", // Required for CORS support to work
                "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
              },
            }
          );
          const responseData1 = await response.json();
          setMedia2(JSON.parse(responseData1.body)[0]);
          const response2 = await fetch(
            `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/search?albums_for_song_id='${id}'`,
            {
              mode: "cors",
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`,
                "Access-Control-Allow-Origin": "*", // Required for CORS support to work
                "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
              },
            }
          );
          const responseData2 = await response2.json();
          setMedia3(JSON.parse(responseData2.body)[0]);
        }
      } catch (error) {
        console.log(error.message);
      }
    };
    loadMedia(id, mediaType);
  }, [id, mediaType]);

  // Check when media changes to update Reviews
  useEffect(() => {
    let external_media_temp = null;
    const loadExternalMedia = async (id, mediaType) => {
      try {
        const token = await getAccessTokenSilently();
        const response = await fetch(
          `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/search?external_url_for_${mediaType}_id=${id}`,
          {
            mode: "cors",
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Access-Control-Allow-Origin": "*", // Required for CORS support to work
              "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
            },
          }
        );

        const responseData = await response.json();

        if (responseData !== undefined && responseData[0].statusCode === 200) {
          setExternalMedia(JSON.parse(responseData[0].body));
        }
        if (responseData !== undefined && responseData[1].statusCode === 200) {
          setExternalMedia2(JSON.parse(responseData[1].body));
        } else {
          if (mediaType === "song") {
            loadExternalMedia2();
          } else {
            setExternalMedia2(null);
          }
        }

        // setExternalMedia(JSON.parse(responseData.body));
      } catch (error) {
        setExternalMedia(external_media_temp);
      }
    };
    setExternalMedia2(null);
    loadExternalMedia(id, mediaType);

    const loadReviews = async (id, mediaType) => {
      try {
        const token = await getAccessTokenSilently();
        const response = await fetch(
          `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/review?${mediaType}_id='${id}'`,
          {
            mode: "cors",
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
              "Access-Control-Allow-Origin": "*", // Required for CORS support to work
              "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
            },
          }
        );
        const responseData = await response.json();

        if (responseData.body !== "{}") {
          setReviews(JSON.parse(responseData.body).reverse());
        }
      } catch (error) {
        console.log(error.message);
      }
    };
    loadReviews(id, mediaType);
  }, [media, media2]);

  const loadExternalMedia2 = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(
        `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/search?streaming_search_term='${
          media.title + " - " + media2.full_name
        }&streaming_service_id=55'`,
        {
          mode: "cors",
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Access-Control-Allow-Origin": "*", // Required for CORS support to work
            "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
          },
        }
      );

      const responseData = await response.json();
      if (
        JSON.parse(responseData.body)[0].statusCode !== 404 &&
        JSON.parse(responseData.body)[0].song.length === 1
      ) {
        setExternalMedia2(JSON.parse(responseData.body)[0].song[0]);
      } else if (JSON.parse(responseData.body)[0].song.length > 1) {
        window.location.reload(false);
      } else {
        setExternalMedia2(null);
      }
    } catch (error) {
      console.log(error.message);
    }
  };

  const handleScoreChange = ({ target: { value } }) => {
    setScore(value);
  };

  const handleDeleteReview = async (review_id) => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(
        `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/review?review_id='${review_id}'`,
        {
          mode: "cors",
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Access-Control-Allow-Origin": "*", // Required for CORS support to work
            "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
          },
        }
      );
      const responseData = await response.json();

      if (responseData.body !== "{}") {
        setReviews(reviews.filter((review) => review.review_id !== review_id));
      }
    } catch (error) {
      console.log(error.message);
    }
  };

  // Handle on change form
  const handleFormChange = (e) => {
    setFormState({
      ...formState,
      [e.target.name]: e.target.value,
      user_id: !isLoading && isAuthenticated ? wufrUser.user_id : "",
      media_type: !isLoading && isAuthenticated ? mediaType : "",
      media_id: !isLoading && isAuthenticated ? id : "",
    });
  };

  const handleCreateReview = async () => {
    try {
      // Validate form data before sending to server
      if (formState.title === "") {
        alert("Please enter title of review");
        return;
      }
      if (formState.description === "") {
        alert("Please enter description of review");
        return;
      }

      let form = { ...formState, score: score };
      const token = await getAccessTokenSilently();
      const response = await fetch(
        `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/review?id='${user.sub}'`,
        {
          mode: "cors",
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Access-Control-Allow-Origin": "*", // Required for CORS support to work
            "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
          },
          body: JSON.stringify(form),
        }
      );

      const responseData = await response.json();
      let review = await JSON.parse(responseData.body);
      let reviewsCopy = [...reviews, review];
      setReviews(reviewsCopy.reverse());
    } catch (error) {
      console.log(error.message);
    }
  };

  const performSearch = async (searchText) => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(
        `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/search?term='${searchText}'`,
        {
          mode: "cors",
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Access-Control-Allow-Origin": "*", // Required for CORS support to work
            "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
          },
        }
      );

      const responseData = await response.json();

      return JSON.parse(responseData.body);
    } catch (error) {
      console.log(error.message);
    }
  };

  // // Call Api
  const onSearch = async () => {
    // check search text length
    if (options !== undefined && value.length > 3) {
      // Search
      let response = await performSearch(value);
      if (response.status === undefined) {
        setOptions(response);
      }
      // Check if response is an array
    }
  };

  const onChange = (data) => {
    setValue(data);
  };

  function msToMinutes(ms) {
    var minutes = Math.floor(ms / 60000);
    var seconds = ((ms % 60000) / 1000).toFixed(0);
    return minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
  }
  const score_options = [
    {
      label: "Like",
      value: 1,
    },
    {
      label: "Dislike",
      value: 0,
    },
  ];

  const calculateAverageScore = () => {
    let total = 0;
    reviews.forEach((review) => {
      total += review.score;
    });

    return (total / reviews.length) * 100 + "%";
  };
  // Effect to check if reviews change
  useEffect(() => {
    if (reviews !== null && reviews.length > 2) {
      setAverageScore(calculateAverageScore());
    } else {
      setAverageScore(null);
    }
  }, [reviews]);

  return (
    <AppLayout>
      <ContentLayout showBorder={isAuthenticated}>
        {!isAuthenticated && !isLoading && (
          <LoginContainer>
            <StyledHeader>Wufr</StyledHeader>
            <StyledSubText>
              Where you can share your thoughts and opinions on the music that
              you listen to.
            </StyledSubText>
            <br></br>
            <StyledSubText>
              Login to get started and start sharing your thoughts on music.
            </StyledSubText>
            <Button
              className="login-button"
              type="primary"
              onClick={() => loginWithRedirect()}
            >
              Login
            </Button>
          </LoginContainer>
        )}
        {isAuthenticated && wufrUser && (
          <LoginContainer>
            <div>
              {mediaType === "song" && (
                <StyledHeader>
                  <span style={{ color: "gray", fontWeight: "300" }}>
                    Song:
                  </span>
                  <br />
                  {media.title}
                </StyledHeader>
              )}
              {mediaType === "album" && (
                <StyledHeader>
                  <span style={{ color: "gray", fontWeight: "300" }}>
                    Album:
                  </span>
                  <br />
                  {media.title}
                </StyledHeader>
              )}
              {media !== undefined && media.artwork !== undefined && (
                <img
                  style={{
                    width: "100%",
                    margin: "1rem auto",
                    borderRadius: "10px",
                  }}
                  src={find640(JSON.parse(media.artwork))}
                  title={media.title}
                />
              )}
              <StyledSubText>
                Artist: <br />
                <span style={{ opacity: "0.7", color: "black" }}>
                  {media2.full_name}
                </span>
                <br />
                {mediaType === "song" && (
                  <span style={{ marginTop: "1rem" }}>
                    <br />
                    Album: <br />
                    <Link to={`/album/${media3.album_id}`}>{media3.title}</Link>
                  </span>
                )}
              </StyledSubText>
              <StyledSubText>
                Release Date: <br />
                <span style={{ opacity: "0.7", color: "black" }}>
                  {media.released_date}
                </span>
              </StyledSubText>

              <StyledSubText style={{ marginBottom: "5rem" }}>
                {media.duration_ms !== undefined && (
                  <>
                    Length:
                    <span style={{ opacity: "0.7", color: "black" }}>
                      {msToMinutes(media.duration_ms)}{" "}
                    </span>
                  </>
                )}
                {media.total_tracks !== undefined && (
                  <>
                    Total Tracks:
                    <span style={{ opacity: "0.7", color: "black" }}>
                      {media.total_tracks}
                    </span>
                  </>
                )}
              </StyledSubText>
            </div>
            <div style={{ marginLeft: "3rem" }}>
              <StyledSubText>Search for different media...</StyledSubText>
              <StyledSearchBarContainer>
                <AutoComplete
                  value={value}
                  style={{
                    width: "100%",
                  }}
                  onSearch={onSearch}
                  onChange={onChange}
                  placeholder="Search for music, artists, etc."
                >
                  {options !== undefined &&
                    options.length > 0 &&
                    options[0].status === undefined &&
                    options.map((item) => (
                      <>
                        <Option key={item[0].song.song_id}>
                          <Link to={`/song/${item[0].song.song_id}`}>
                            <div>
                              <img
                                width="100px"
                                title="Song Image"
                                src={find640(JSON.parse(item[0].song.artwork))}
                              />
                              <p>
                                <Link to={`/song/${item[0].song.song_id}`}>
                                  {item[0].song.title}
                                </Link>{" "}
                                <span style={{ opacity: ".7" }}>
                                  {" "}
                                  - {item[0].artists[0].full_name} -{" "}
                                  <Link to={`/album/${item[0].album.album_id}`}>
                                    {item[0].album.title}
                                  </Link>
                                </span>
                              </p>
                            </div>
                          </Link>
                        </Option>
                        <Option key={item[1].song.song_id}>
                          <Link to={`/song/${item[1].song.song_id}`}>
                            <div>
                              <img
                                width="100px"
                                title="Song Image"
                                src={find640(JSON.parse(item[1].song.artwork))}
                              />
                              <p>
                                <Link to={`/song/${item[1].song.song_id}`}>
                                  {item[0].song.title}
                                </Link>{" "}
                                <span style={{ opacity: ".7" }}>
                                  {" "}
                                  - {item[1].artists[0].full_name} -{" "}
                                  <Link to={`/album/${item[1].album.album_id}`}>
                                    {item[1].album.title}
                                  </Link>
                                </span>
                              </p>
                            </div>
                          </Link>
                        </Option>
                        <Option key={item[2].song.song_id}>
                          <Link to={`/song/${item[2].song.song_id}`}>
                            <div>
                              <img
                                width="100px"
                                title="Song Image"
                                src={find640(JSON.parse(item[2].song.artwork))}
                              />
                              <p>
                                <Link to={`/song/${item[2].song.song_id}`}>
                                  {item[2].song.title}
                                </Link>{" "}
                                <span style={{ opacity: ".7" }}>
                                  {" "}
                                  - {item[2].artists[0].full_name} -{" "}
                                  <Link to={`/album/${item[1].album.album_id}`}>
                                    {item[2].album.title}
                                  </Link>
                                </span>
                              </p>
                            </div>
                          </Link>
                        </Option>
                      </>
                    ))}
                </AutoComplete>
              </StyledSearchBarContainer>

              {external_media !== undefined &&
                external_media !== null &&
                external_media.external_id !== undefined && (
                  <>
                    <StyledSubText style={{ marginBottom: "1rem" }}>
                      Link to streaming platforms:
                    </StyledSubText>{" "}
                    <iframe
                      src={`https://open.spotify.com/embed?uri=${external_media.external_id}`}
                      width="100%"
                      height="380"
                      frameborder="0"
                      style={{ borderRadius: "10px" }}
                      allowtransparency="true"
                      allow="encrypted-media"
                    ></iframe>
                  </>
                )}

              {external_media2 !== undefined &&
                external_media2 !== null &&
                external_media2.external_id !== undefined && (
                  <iframe
                    id="ytplayer"
                    type="text/html"
                    width="100%"
                    height="380"
                    style={{ borderRadius: "10px" }}
                    src={`https://www.youtube.com/embed/${external_media2.external_id}`}
                    frameborder="0"
                  ></iframe>
                )}

              {media !== undefined && <StyledSubText>Reviews:</StyledSubText>}
              {averageScore !== null && (
                <StyledSubText>Average Score: {averageScore}</StyledSubText>
              )}
              <div
                style={{
                  overflowY: "scroll",
                  maxHeight: "300px",
                }}
              >
                {reviews !== undefined &&
                  Array.isArray(reviews) &&
                  reviews.length > 0 && (
                    <div>
                      {reviews.map((review) => (
                        <Card
                          title={review.title}
                          style={{
                            width: "100%",
                            marginTop: "1rem",
                            background: review.score ? "#e6ffed" : "#fff1f0",
                          }}
                        >
                          <p>{review.description}</p>
                          {review.user_id === wufrUser.user_id && (
                            <Button
                              style={{ padding: "5px", marginTop: "5px" }}
                              onClick={() =>
                                handleDeleteReview(review.review_id)
                              }
                            >
                              <DeleteOutlined />
                            </Button>
                          )}
                        </Card>
                      ))}
                    </div>
                  )}
              </div>
              {media !== undefined && (
                <Button
                  type="primary"
                  style={{
                    width: "100%",
                    marginTop: "1rem",
                    marginBottom: "5rem",
                  }}
                  onClick={showModal}
                >
                  Add Review
                </Button>
              )}

              {reviews === null && (
                <div>
                  <StyledSubText>
                    No reviews for this {mediaType} yet. Be the first to review
                    this {mediaType}!
                  </StyledSubText>
                </div>
              )}
            </div>
          </LoginContainer>
        )}
        <Modal
          title="Create Review"
          visible={isModalOpen}
          onOk={handleOk}
          okText="Submit"
          onCancel={handleCancel}
        >
          {/* Get Title Input*/}
          <StyledInput
            id="title"
            style={{ width: "100%" }}
            name="title"
            value={formState.title}
            onChange={(e) => handleFormChange(e)}
            placeholder="Title"
          />
          {/* Get Description Input*/}
          <StyledInput
            // rows={10}
            id="description"
            name="description"
            style={{ width: "100%" }}
            rows={10}
            value={formState.description}
            onChange={(e) => handleFormChange(e)}
            placeholder="Write your review here..."
          />
          <p style={{ opacity: "0.7", margin: "1rem auto 1rem auto" }}>
            Is it worth a listen?
          </p>
          {/* Get Score Input*/}
          <Radio.Group
            id="score"
            name="score"
            options={score_options}
            onChange={handleScoreChange}
            value={score}
            optionType="button"
          />
        </Modal>
      </ContentLayout>
    </AppLayout>
  );
};

export default MediaPage;
