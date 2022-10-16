import React from "react";
import { useEffect, useState } from "react";
import { Routes, Route, useParams, Link } from "react-router-dom";
import Home from "./routes/home";
import Register from "./routes/register";
import styled from "styled-components";
import Logo from "./components/logo";
import "antd/dist/antd.css";
import { Layout, Button, Tooltip } from "antd";
import MediaPage from "./routes/mediaPage";
import { useAuth0 } from "@auth0/auth0-react";

const { Header } = Layout;

const MainContainer = styled.main`
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  font-family: Geneva, Verdana, sans-serif;
`;

const AppLayout = styled(Layout)`
  min-height: 100%;

  .app-header {
    background-color: #0c2e52;
    height: 8rem;
    padding: 2rem 2rem;
    color: white;
  }

  .login-button {
    color: white;
    font-size: 1.5rem;
    height: 4rem;
    line-height: 1;
    background-color: #3cb989;
    padding: 1rem;
    &:hover {
      opacity: 90%;
    }
  }

  .logout-button {
    color: white;
    font-size: 1.5rem;
    height: 4rem;
    line-height: 1;
    background-color: #fc394d;
    padding: 1rem;
    &:hover {
      opacity: 90%;
    }
  }
`;

const NavBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

// Main Application Container
const App = () => {
  // Use state for logined user
  const [wufrUser, setWufrUser] = useState(null);
  const {
    isAuthenticated,
    isLoading,
    loginWithRedirect,
    user,
    getAccessTokenSilently,
    logout,
  } = useAuth0();

  const { id } = useParams();

  // Use Effect to make GET api call using fetch to get user data by using getAccessTokenSilently
  useEffect(async () => {
    const getUserData = async () => {
      try {
        const token = await getAccessTokenSilently();
        const response = await fetch(
          `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/users?id='${user.sub}'`,
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

        setWufrUser(responseData.user);
        return responseData.user;
      } catch (error) {
        console.log(error.message);
      }
    };

    if (
      user &&
      isAuthenticated &&
      wufrUser === null &&
      window.location.href !== window.location.origin + "/register"
    ) {
      let response = await getUserData();

      if (response === null) {
        window.location.href = "/register";
      }
    }
  }, [user, wufrUser]);

  return (
    <MainContainer>
      <AppLayout>
        <Header theme="light" className="app-header">
          <NavBar>
            <Link to="/">
              <Logo></Logo>
            </Link>
            {!isAuthenticated && !isLoading && (
              <Tooltip title="Login">
                <Button
                  type="link"
                  onClick={() => loginWithRedirect()}
                  className="login-button"
                >
                  Login SSO
                </Button>
              </Tooltip>
            )}
            {isAuthenticated && !isLoading && (
              <Tooltip title="Logout">
                <Button
                  type="link"
                  onClick={() =>
                    logout({ returnTo: "https://damianbarrous.com/" })
                  }
                  className="logout-button"
                >
                  Logout
                </Button>
              </Tooltip>
            )}
          </NavBar>
        </Header>
        <Routes>
          <Route
            path="/"
            element={
              <Home
                isAuthenticated={isAuthenticated}
                isLoading={isLoading}
                loginWithRedirect={loginWithRedirect}
                user={user}
                wufrUser={wufrUser}
                getAccessTokenSilently={getAccessTokenSilently}
              />
            }
            exact
          />
          <Route
            path="/register"
            element={
              <Register
                isAuthenticated={isAuthenticated}
                isLoading={isLoading}
                loginWithRedirect={loginWithRedirect}
                user={user}
                wufrUser={wufrUser}
                setWufrUser={setWufrUser}
                getAccessTokenSilently={getAccessTokenSilently}
              />
            }
            exact
          />
          <Route
            path="/song/:id"
            element={
              <MediaPage
                isAuthenticated={isAuthenticated}
                isLoading={isLoading}
                loginWithRedirect={loginWithRedirect}
                user={user}
                wufrUser={wufrUser}
                getAccessTokenSilently={getAccessTokenSilently}
                id={id}
                mediaType="song"
              />
            }
          />
          <Route
            path="/album/:id"
            element={
              <MediaPage
                isAuthenticated={isAuthenticated}
                isLoading={isLoading}
                loginWithRedirect={loginWithRedirect}
                user={user}
                wufrUser={wufrUser}
                getAccessTokenSilently={getAccessTokenSilently}
                id={id}
                mediaType="album"
              />
            }
          />
        </Routes>
      </AppLayout>
    </MainContainer>
  );
};

export default App;
