"""
MenoMind - CSS Styles Module
Contains all the CSS styling for the application
"""

def load_css_styles():
    """
    Returns the CSS styles for the application
    """
    return """
    <style>
        /* Remove blank space at top and bottom */ 
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
        }
        
        /* Main content styling */
        .main-content {
            background-color: #fcf7fa;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 0px; 
        }
        
        /* Chat message styling */
        .chat-message {
            padding: 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            position: relative;
        }
        
        .user-message {
            background-color: #f0f7ff;
            border-left: 5px solid #7c89ff;
        }
        
        .assistant-message {
            background-color: #fff0f9;
            border-left: 5px solid #FF69B4;
        }
        
        /* Card styling */
        .info-card {
            background-color: white;
            border: 1px solid #FF69B4;
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #FF69B4;
        }
        
        div.stButton > button:first-child {
            background-color: #f8f2f6;
            border: 1px solid #000000;
            border-radius: 20px;
            padding: 8px 16px;
            margin: 5px 0;
            font-size: 0.85rem;
            color: black;
            cursor: pointer;
            transition: all 0.2s;
        }

        div.stButton > button:first-child:hover {
            background-color: #ffcce6;
            border: 1px solid #000000;
            color: #000000;
        }
        
        .stFormSubmitButton > button {
            background-color: #f8f2f6;
            border: 1px solid #000000;
            border-radius: 20px;
            padding: 8px 16px;
            margin: 5px 0;
            font-size: 0.85rem;
            color: black;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .stFormSubmitButton > button:hover {
            background-color: #ffcce6;
            border: 1px solid #000000;
            color: #000000;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #fcf0f6;
            border-radius: 8px 8px 0 0;
            padding: 10px 16px;
            border: none;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #ff9fce !important;
            color: white !important;
        }
        
        /* Quick question chips */
        .quick-question {
            display: inline-block;
            background-color: #f8f2f6;
            border: 1px solid #000000;
            border-radius: 20px;
            padding: 8px 16px;
            margin: 5px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .quick-question:hover {
            background-color: #ffcce6;
        }
        
        /* Resource card styling */
        .resource-card {
            background-color: white;
            border: 1px solid #FF69B4;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #FF69B4;
            padding: 10px;
            margin: 10px 10px 10px 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.2s;
        }
        
        .resource-card:hover {
            transform: translateY(-5px);
        }
        
        /* Footer styling */
        .fixed-bottom-warning {
            position: fixed;
            background-color: #f8f2f6;
            border: 1px solid black;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 10px;
            margin-left: 120px;
            text-align: center;
            font-size: 10px;
            font-weight: 600;
            font-family: "Dancing Script", cursive;
            z-index: 1000;
        }
    </style>
    """