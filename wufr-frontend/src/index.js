import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles/reset.css";
import { Auth0Provider } from "@auth0/auth0-react";

ReactDOM.render(
  <Auth0Provider
    domain="dev-6nrcob3m.auth0.com"
    clientId="69DP2osu32Qq4ydDvcDRWtlaNDNtS2la"
    redirectUri={window.location.origin}
    audience="https://helloauthorizer.com"
  >
    <React.StrictMode>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </React.StrictMode>
  </Auth0Provider>,
  document.getElementById("root")
);
