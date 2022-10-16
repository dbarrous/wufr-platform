import React from "react";
import { useState, useEffect } from "react";
import { Layout, AutoComplete, Button } from "antd";
import styled from "styled-components";

// import react router link
import { Link } from "react-router-dom";
const { Option } = AutoComplete;

const AppLayout = styled(Layout)`
  height: 100%;

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

const ContentLayout = styled(Layout)`
  border-top-left-radius: ${(props) => (props.showBorder ? "10px" : "none")};
  background: #f3f8fc;
`;

const LoginContainer = styled.div`
  margin: auto;
  margin-top: 5em;
  color: #b0b0b0;
  display: flex;
  flex-flow: column;
`;

const StyledHeader = styled.h1`
  color: #05b6ec;
  font-size: 5rem;
  font-weight: 700;
  text-align: center;
`;

const StyledSubheader = styled.h3`
  color: #05b6ec;
  font-size: 2rem;
  font-weight: 700;
  margin-top: 2rem;
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
  width: 80%;
  height: 5rem;
  padding: 0 1rem;
  margin: auto;
  margin-top: 1rem;
`;

const Home = (props) => {
  const {
    isAuthenticated,
    isLoading,
    loginWithRedirect,
    wufrUser,
    getAccessTokenSilently,
  } = props;

  const [value, setValue] = useState("");
  const [options, setOptions] = useState([]);
  const [reviewCount, setReviewCount] = useState(0);
  // Effect for load
  useEffect(async () => {
    if (wufrUser) {
      const token = await getAccessTokenSilently();
      const response = await fetch(
        `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/review?user_id='${wufrUser.user_id}'`,
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
      const data = await response.json();
      if (data.body !== "{}") {
        console.log(JSON.parse(data.body));
        setReviewCount(JSON.parse(data.body).length);
      }
    }
  }, [wufrUser]);
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
      console.log(JSON.parse(responseData.body));
      console.log(window.location.href);
      return JSON.parse(responseData.body);
    } catch (error) {
      console.log(error.message);
    }
  };
  // // Call Api
  const onSearch = async (searchText) => {
    // check search text length
    if (options !== undefined && value.length > 3 && value.length % 2 === 0) {
      // Search
      let response = await performSearch(value);
      console.log(response);
      if (response.status === undefined) {
        setOptions(response);
      }
      // Check if response is an array
    }
  };

  const onChange = (data) => {
    setValue(data);
  };
  // Find 640 image in array of images
  const find640 = (images) => {
    let image = images.find((image) => image.width === 640);
    return image.url;
  };
  // // Effect to check is options has changed
  useEffect(() => {
    console.log("Options changed");
    console.log(options);
  }, [options]);

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
            <StyledHeader>Wufr</StyledHeader>
            <StyledSubText>
              Where you can share your thoughts and opinions on the music that
              you listen to.
            </StyledSubText>
            <br></br>
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
            <StyledSubText>
              Hi <span style={{ color: "#0c2e52" }}>{wufrUser.full_name}</span>,
              you are logged in!{" "}
            </StyledSubText>
            <StyledSubheader>Your Review Stats</StyledSubheader>
            <StyledSubText>
              You have reviewed{" "}
              <span style={{ color: "#0c2e52" }}>{reviewCount}</span> times.
            </StyledSubText>
            <StyledSubheader>Your Playlists</StyledSubheader>
            <StyledSubText>
              Front-end of Playlist currently under construction - Coming Soon!
            </StyledSubText>
          </LoginContainer>
        )}
      </ContentLayout>
    </AppLayout>
  );
};

export default Home;
