import streamlit as st
import tweepy
import os
import webbrowser

# ------------------------------------------------------------------
# 1. Twitter App credentials (OAuth 2.0 Client ID & Secret)
# ------------------------------------------------------------------
CLIENT_ID = "ZEpPOUdUakhQdTR4b2drTFdremg6MTpjaQ"
CLIENT_SECRET = "oQ3aWBZbNqpM3GXQz6hn-FcST-pLeUoKpVMMLKfK_744cANvR-"
REDIRECT_URI = "https://imager123.streamlit.app/"  # Change this to match your Twitter app settings

# ------------------------------------------------------------------
# OAuth2 User Authentication with PKCE
# ------------------------------------------------------------------
def authenticate_user():
    """Authenticate the user with Twitter using OAuth 2.0."""
    auth = tweepy.OAuth2UserHandler(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=["tweet.read", "tweet.write", "users.read", "offline.access"]
    )

    # Generate authorization URL
    auth_url = auth.get_authorization_url()
    
    # Show login link
    st.write("Click the link below to log in with Twitter:")
    st.markdown(f"[Login with Twitter]({auth_url})")
    
    # Get the authorization response from the user
    authorization_response = st.text_input("Paste the full URL you were redirected to after authorization:")

    if st.button("Authenticate"):
        if authorization_response:
            try:
                access_token = auth.fetch_token(authorization_response)
                st.session_state["access_token"] = access_token["access_token"]
                st.success("Authentication successful!")
            except Exception as e:
                st.error(f"Error authenticating: {e}")

# ------------------------------------------------------------------
# Use Twitter API with OAuth 2.0 Token
# ------------------------------------------------------------------
def get_twitter_api():
    """Return a Tweepy API object if authenticated."""
    if "access_token" in st.session_state:
        auth = tweepy.Client(
            bearer_token=st.session_state["access_token"]
        )
        return auth
    return None

# ------------------------------------------------------------------
# Post Tweets or Upload Images
# ------------------------------------------------------------------
def post_tweet():
    """Post a simple tweet to Twitter."""
    api = get_twitter_api()
    if api:
        tweet_text = st.text_area("Write your tweet")
        if st.button("Post Tweet"):
            try:
                api.create_tweet(text=tweet_text)
                st.success("Tweet posted successfully!")
            except Exception as e:
                st.error(f"Failed to post tweet: {e}")
    else:
        st.warning("Please authenticate first.")

# ------------------------------------------------------------------
# Main Streamlit App
# ------------------------------------------------------------------
def main():
    st.title("Twitter OAuth 2.0 Login & Tweet App")
    
    # Step 1: Authenticate the user
    if "access_token" not in st.session_state:
        authenticate_user()
    else:
        st.success("You are already logged in!")
        post_tweet()

if __name__ == "__main__":
    main()
