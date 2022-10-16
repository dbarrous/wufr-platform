import React from "react";
import styled from "styled-components";
import logo from "../assets/wufr_logo.svg";
import { Image } from "antd";

const Wrapper = styled.div`
  display: flex;
  align-items: flex-start;

  .logo-img {
    height: 4.5rem;
    filter: brightness(5);
    color: white;
  }
`;

const Title = styled.h3`
  color: #f3f8fc;
  margin-left: 1.5rem;
  font-family: "Roboto", sans-serif;
  font-size: 3rem;
`;

const Logo = () => {
  return (
    <Wrapper>
      <Image className="logo-img" src={logo} preview={false} />
      <Title>Wufr</Title>
    </Wrapper>
  );
};

export default Logo;
