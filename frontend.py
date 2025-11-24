"""
Streamlit Frontend for the Simple Social application.

This file contains the entire user interface, built with Streamlit. It handles:
- User authentication (login and registration).
- A feed page to display all posts.
- An upload page for creating new posts.
- Dynamic media transformations using ImageKit.io for overlays.

All communication with the backend is done via HTTP requests to the FastAPI API.
"""
import streamlit as st
import requests
import base64
import urllib.parse

st.set_page_config(page_title="Simple Social", layout="wide")

# Initialize session state to persist user login status across reruns.
# `st.session_state` acts like a dictionary that holds data for a user session.
if 'token' not in st.session_state:
    st.session_state.token = None  # Stores the JWT for API requests.
if 'user' not in st.session_state:
    st.session_state.user = None   # Stores user information (email, id).


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    """Displays the login and registration page.

    This page shows input fields for email and password. It provides two buttons:
    - Login: Authenticates the user via the `/auth/jwt/login` endpoint.
    - Sign Up: Registers a new user via the `/auth/register` endpoint.
    On successful login, it saves the user's token and data to the session state.
    """
    st.title("🚀 Welcome to Simple Social")

    # Simple form with two buttons
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                # Login using FastAPI Users JWT endpoint
                login_data = {"username": email, "password": password}
                response = requests.post("http://localhost:8000/auth/jwt/login", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]

                    # Get user info
                    user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password!")

        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                # Register using FastAPI Users
                signup_data = {"email": email, "password": password}
                response = requests.post("http://localhost:8000/auth/register", json=signup_data)

                if response.status_code == 201:
                    st.success("Account created! Click Login now.")
                else:
                    error_detail = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error_detail}")
    else:
        st.info("Enter your email and password above")


def upload_page():
    """Displays the page for uploading a new post.

    Provides a file uploader for images/videos and a text area for a caption.
    When the user clicks 'Share', it sends a multipart/form-data request to the
    `/upload` endpoint of the backend API.
    """
    st.title("📸 Share Something")

    uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
    caption = st.text_area("Caption:", placeholder="What's on your mind?")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            response = requests.post("http://localhost:8000/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 200:
                st.success("Posted!")
                st.rerun()
            else:
                st.error("Upload failed!")


def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 then URL encode"""
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    """Constructs a dynamic ImageKit.io URL for media transformations.

    This function takes a base ImageKit URL and adds transformation parameters.
    It has special logic to create a text overlay for image captions.

    Args:
        original_url (str): The base URL of the media from ImageKit.
        transformation_params (str): A string of ImageKit transformation parameters.
        caption (str, optional): If provided, a text overlay for the caption will be
                                 added to the image transformation.

    Returns:
        str: The new URL with the transformation parameters applied.
    """
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        # Add text overlay at bottom with semi-transparent background
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-80,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    parts = original_url.split("/")

    imagekit_id = parts[3]
    file_path = "/".join(parts[4:])
    base_url = "/".join(parts[:4])
    return f"{base_url}/tr:{transformation_params}/{file_path}"


def feed_page():
    """Displays the main feed of all posts.

    Fetches all posts from the `/feed` endpoint. For each post, it displays the
    author's email, the creation date, and the media (image or video).
    If the current user is the owner of a post, a delete button is shown, which
    calls the `/posts/{post_id}` endpoint.
    """
    st.title("🏠 Feed")

    response = requests.get("http://localhost:8000/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()["posts"]

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        for post in posts:
            st.markdown("---")

            # Header with user, date, and delete button (if owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{post['email']}** • {post['created_at'][:10]}")
            with col2:
                if post.get('is_owner', False):
                    if st.button("🗑️", key=f"delete_{post['id']}", help="Delete post"):
                        # Delete the post
                        response = requests.delete(f"http://localhost:8000/posts/{post['id']}", headers=get_headers())
                        if response.status_code == 200:
                            st.success("Post deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete post!")

            # Uniform media display with caption overlay
            caption = post.get('caption', '')
            if post['file_type'] == 'image':
                uniform_url = create_transformed_url(post['url'], "", caption)
                st.image(uniform_url, width=300)
            else:
                # For videos: specify only height to maintain aspect ratio + caption overlay
                uniform_video_url = create_transformed_url(post['url'], "w-400,h-200,cm-pad_resize,bg-blurred")
                st.video(uniform_video_url, width=300)
                st.caption(caption)

            st.markdown("")  # Space between posts
    else:
        st.error("Failed to load feed")


# --- Main Application Logic ---
# This block controls which page is displayed based on the user's login status.

if st.session_state.user is None:
    # If the user is not logged in, show the login page.
    login_page()
else:
    # If the user is logged in, display the main app with sidebar navigation.
    st.sidebar.title(f"👋 Hi {st.session_state.user['email']}!")

    if st.sidebar.button("Logout"):
        # Clear session state on logout and rerun the script to show the login page.
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    
    # Use a radio button in the sidebar for page navigation.
    page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

    # Display the selected page.
    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()