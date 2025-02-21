import streamlit as st
import tweepy
from PIL import Image
import os


CONSUMER_KEY = "1jumvRUJ8LnBCUbyFJHmZVgQH"
CONSUMER_SECRET = "2Vjuazcwdv3oBGNAsvZ220FqmBWxBVFunaeWEs3lGggL5EpMy7"


def get_twitter_api():
    """Return a Tweepy API instance if the user is authenticated; otherwise None."""
    if "access_token" in st.session_state and "access_token_secret" in st.session_state:
        auth = tweepy.OAuth1UserHandler(
            CONSUMER_KEY,
            CONSUMER_SECRET,
            st.session_state["access_token"],
            st.session_state["access_token_secret"]
        )
        return tweepy.API(auth)
    return None


def handle_pin_based_flow():
    st.subheader("1. Authenticate with Twitter via PIN-Based OAuth")

    
    if "request_token" not in st.session_state:
        st.session_state["request_token"] = None

    
    if st.button("Start Twitter OAuth Flow"):
        auth = tweepy.OAuth1UserHandler(
            CONSUMER_KEY,
            CONSUMER_SECRET,
            callback="oob"  
        )
        try:
            redirect_url = auth.get_authorization_url()
            st.session_state["request_token"] = auth.request_token
            st.write("**Step:** Click the link below to authorize this app on Twitter:")
            st.markdown(f"[Authorize on Twitter]({redirect_url})")
        except tweepy.TweepyException as e:
            st.error(f"Error! Failed to get request token: {e}")

    
    pin = st.text_input("Enter the PIN from Twitter")

    
    if st.button("Verify PIN"):
        if st.session_state.get("request_token") is None:
            st.warning("You need to start the OAuth flow first (request token is missing).")
        else:
            auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.request_token = st.session_state["request_token"]
            try:
                auth.get_access_token(pin)
                
                st.session_state["access_token"] = auth.access_token
                st.session_state["access_token_secret"] = auth.access_token_secret
                st.success("Authentication successful! You are now logged into Twitter.")
            except tweepy.TweepyException as e:
                st.error(f"Failed to get access token: {e}")


def handle_image_resize_and_publish():
    st.subheader("2. Image Resizer & Publisher")

    
    uploaded_file = st.file_uploader("Choose an image file:", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        try:
            
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
        except Exception as e:
            st.error("Error loading the image. Please try again with a valid image format.")
            st.stop()

        
        default_sizes = {
            "300x250": (300, 250),
            "728x90": (728, 90),
            "160x600": (160, 600),
            "300x600": (300, 600)
        }

        
        st.write("Configure Desired Dimensions (Optional):")
        custom_sizes = {}
        for label, (w, h) in default_sizes.items():
            col1, col2 = st.columns(2)
            with col1:
                new_w = st.number_input(f"Width for {label}", value=w, step=1)
            with col2:
                new_h = st.number_input(f"Height for {label}", value=h, step=1)
            custom_sizes[label] = (new_w, new_h)

        
        st.subheader("Resized Images Preview")
        resized_images = {}
        for label, (width, height) in custom_sizes.items():
            try:
                resized_img = image.resize((width, height))
                resized_images[label] = resized_img
                st.image(
                    resized_img,
                    caption=f"{label}: {width}x{height}",
                    use_container_width=False
                )
            except Exception as e:
                st.error(f"Error resizing image for {label}: {e}")

        
        if st.button("Publish Images to X"):
            api = get_twitter_api()
            if api is None:
                st.warning("You must first authenticate with Twitter (PIN-based OAuth) before publishing.")
            else:
                try:
                    for label, img in resized_images.items():
                        filename = f"temp_{label}.png"
                        img.save(filename)
                        status_text = f"Posting a resized image: {label} ({width}x{height})"
                        api.update_status_with_media(status=status_text, filename=filename)
                        os.remove(filename)
                    st.success("All images have been published to your X (Twitter) account!")
                except Exception as e:
                    st.error(f"Failed to publish images: {e}")
    else:
        st.info("Please upload an image file to resize and publish.")


def main():
    st.title("Streamlit App: PIN-Based Twitter OAuth + Image Resizer")
    st.write(
        "This app demonstrates how to authenticate with Twitter (X) "
        "using PIN-based OAuth, then upload, resize, and publish images."
    )

    
    if "access_token" not in st.session_state or "access_token_secret" not in st.session_state:
        handle_pin_based_flow()
    else:
        st.success("✅ You are already authenticated with Twitter!")
        api = get_twitter_api()
        if api:
            try:
                user = api.me()
                st.write(f"Logged in as **@{user.screen_name}**.")
            except Exception as e:
                st.error(f"Error fetching user profile: {e}")

    handle_image_resize_and_publish()


if __name__ == "__main__":
    main()
