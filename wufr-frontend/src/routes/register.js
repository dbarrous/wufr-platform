import React from "react";
import { useState } from "react";
import { Layout, Input, Button, Checkbox } from "antd";
import styled from "styled-components";

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

const StyledSubText = styled.p`
  width: 70%;
  color: #b0b0b0;
  font-size: 1.5rem;
  text-align: center;
  margin: auto;
  margin-top: 1rem;
`;

// Styled controlled Input
const StyledInput = styled(Input)`
  width: 50%;
  margin: auto;
  margin-top: 1rem;
`;

//Styled Checkbox controlled Input
const StyledCheckbox = styled(Checkbox)`
  width: 50%;
  margin: auto;
  margin-top: 1rem;
`;

// React component thith state that is a registration form antd
const Register = (props) => {
  const {
    isAuthenticated,
    isLoading,
    setWufrUser,
    user,
    getAccessTokenSilently,
  } = props;

  // State for the form
  const [formState, setFormState] = useState({
    full_name: "",
    over_18: false,
  });

  // Handle on change form
  const handleFormChange = (e) => {
    if (e.target.name === "over_18") {
      setFormState({
        ...formState,
        [e.target.name]: e.target.checked,
        email: !isLoading && isAuthenticated ? user.email : "",
        autho_id: !isLoading && isAuthenticated ? user.sub : "",
      });
    } else {
      setFormState({
        ...formState,
        [e.target.name]: e.target.value,
        email: !isLoading && isAuthenticated ? user.email : "",
        autho_id: !isLoading && isAuthenticated ? user.sub : "",
      });
    }
  };

  const handleRegister = async () => {
    try {
      // Validate form data before sending to server
      if (formState.full_name === "") {
        alert("Please enter your full name");
        return;
      }
      if (formState.over18 === false) {
        alert("You must be over 18 to register");
        return;
      }
      const token = await getAccessTokenSilently();
      const response = await fetch(
        `https://b9yv8tlybd.execute-api.us-east-1.amazonaws.com/users?id='${user.sub}'`,
        {
          mode: "cors",
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Access-Control-Allow-Origin": "*", // Required for CORS support to work
            "Access-Control-Allow-Credentials": true, // Required for cookies, authorization headers with HTTPS
          },
          body: JSON.stringify(formState),
        }
      );

      const responseData = await response.json();

      const parsed = await JSON.parse(responseData.body);

      if ((await parsed.user) !== null) {
        setWufrUser(parsed.user);
        //redirect to home
        window.location.href = "/";
      } else {
        setWufrUser(parsed.user);
        //redirect to home
        window.location.href = "/";
      }
    } catch (error) {
      console.log(error.message);
    }
  };

  return (
    <AppLayout>
      <ContentLayout>
        <LoginContainer>
          <StyledHeader>Welcome!</StyledHeader>
          <StyledSubText>
            To start using Wufr, please answer the following questions:
          </StyledSubText>
          {/* Get Full Name Input*/}
          <StyledInput
            id="full_name"
            name="full_name"
            value={formState.full_name}
            onChange={(e) => handleFormChange(e)}
            placeholder="Full Name"
          />

          {/* Check if 18+ to use Checkbox Input*/}
          <StyledCheckbox
            id="over_18"
            name="over_18"
            onChange={(e) => handleFormChange(e)}
          >
            Are you 18 or older?
          </StyledCheckbox>
          <Button className="login-button" onClick={() => handleRegister()}>
            Register
          </Button>
        </LoginContainer>
      </ContentLayout>
    </AppLayout>
  );
};

export default Register;
