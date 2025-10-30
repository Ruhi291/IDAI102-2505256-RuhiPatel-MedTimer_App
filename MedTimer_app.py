import streamlit as st
from datetime import datetime, time
import random

st.set_page_config(page_title="MedTimer", page_icon="💊", layout="centered")

# Custom CSS with WHITE text
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);}
    .main-container {background: rgba(30, 30, 50, 0.95); padding: 30px; border-radius: 25px; 
                     box-shadow: 0 10px 40px rgba(0,0,0,0.5); margin: 20px 0; color: white !important;}
    h1, h2, h3, h4, h5, h6, p, span, div, label {color: white !important;}
    .stButton>button {background: linear-gradient(135deg, #f093fb, #f5576c) !important; 
                      color: white !important; border: none; padding: 15px 40px; font-size: 18px; 
                      border-radius: 50px; font-weight: 700; width: 100%; 
                      box-shadow: 0 5px 20px rgba(240, 147, 251, 0.5);}
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTimeInput>div>div>input, 
    .stSelectbox>div>div>select {background: rgba(50, 50, 70, 0.9) !important; 
                                 color: white !important; border: 2px solid rgba(255, 255, 255, 0.3) !important; 
                                 border-radius: 15px; padding: 12px;}
    .medicine-item {background: rgba(50, 50, 70, 0.8); padding: 20px; border-radius: 15px; 
                    margin: 15px 0; border-left: 6px solid #ddd; color: white !important;}
    .medicine-taken {border-left-color: #00b894; background: rgba(0, 184, 148, 0.2);}
    .medicine-upcoming {border-left-color: #fdcb6e; background: rgba(253, 203, 110, 0.2);}
    .medicine-missed {border-left-color: #ff7675; background: rgba(255, 118, 117, 0.2);}
    .badge-taken {background: linear-gradient(135deg, #00b894, #00cec9); color: white; 
                  padding: 8px 16px; border-radius: 25px; font-size: 13px; font-weight: 700;}
    .badge-upcoming {background: linear-gradient(135deg, #fdcb6e, #ffeaa7); color: #2d3436; 
                     padding: 8px 16px; border-radius: 25px; font-size: 13px; font-weight: 700;}
    .badge-missed {background: linear-gradient(135deg, #ff7675, #fd79a8); color: white; 
                   padding: 8px 16px; border-radius: 25px; font-size: 13px; font-weight: 700;}
    .quote-card {background: linear-gradient(135deg, #ffeaa7, #fdcb6e); padding: 25px; 
                 border-radius: 20px; font-style: italic; color: #2d3436 !important; 
                 box-shadow: 0 5px 20px rgba(253, 203, 110, 0.5); margin: 20px 0; 
                 font-size: 18px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# Initialize
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user_name = None
    st.session_state.user_age = None
    st.session_state.medicines = []
    st.session_state.medicine_status = {}
    st.session_state.current_screen = 'welcome'
    st.session_state.confirm_reset = False

QUOTES = [
    "Your health is an investment, not an expense.",
    "Take care of your body. It's the only place you have to live.",
    "Consistency is key to good health.",
    "Small steps lead to big changes.",
    "Health is wealth. Never forget to take your medicine!",
    "Every pill is a step towards recovery."
]

def get_medicine_status(med_id, med_time):
    now = datetime.now()
    current_time = now.hour * 60 + now.minute
    med_hour, med_min = map(int, med_time.split(':'))
    med_time_mins = med_hour * 60 + med_min
    status = st.session_state.medicine_status.get(med_id, {})
    is_today = status.get('date') == now.strftime('%Y-%m-%d')
    if is_today and status.get('taken', False):
        return 'taken', '✓ Taken', 'badge-taken'
    elif current_time > med_time_mins + 60:
        return 'missed', 'Missed', 'badge-missed'
    else:
        return 'upcoming', 'Upcoming', 'badge-upcoming'

def calculate_adherence():
    if not st.session_state.medicines:
        return 0, 0, 0, 0
    now = datetime.now()
    current_time = now.hour * 60 + now.minute
    taken = upcoming = missed = 0
    for med in st.session_state.medicines:
        med_hour, med_min = map(int, med['time'].split(':'))
        med_time_mins = med_hour * 60 + med_min
        status = st.session_state.medicine_status.get(med['id'], {})
        is_today = status.get('date') == now.strftime('%Y-%m-%d')
        if is_today and status.get('taken', False):
            taken += 1
        elif current_time > med_time_mins + 60:
            missed += 1
        else:
            upcoming += 1
    total = taken + upcoming + missed
    adherence = round((taken / total) * 100) if total > 0 else 0
    return adherence, taken, upcoming, missed

def welcome_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; font-size: 100px;'>💊</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 56px; font-weight: 800;'>MedTimer</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 20px; font-weight: 600;'>Never miss your medicine!</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 16px; margin: 20px 0;'>Take control of your health with smart medication tracking.</p>", unsafe_allow_html=True)
        if st.button("GET STARTED", key="get_started"):
            st.session_state.current_screen = 'setup' if not st.session_state.user_name else 'dashboard'
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def setup_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>👤 Setup Profile</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    name = st.text_input("Your Name", placeholder="Enter your name")
    age = st.number_input("Your Age", min_value=1, max_value=120, value=25)
    if st.button("CONTINUE"):
        if name.strip():
            st.session_state.user_name = name.strip()
            st.session_state.user_age = age
            st.session_state.current_screen = 'dashboard'
            st.rerun()
        else:
            st.error("Please enter your name!")
    st.markdown("</div>", unsafe_allow_html=True)

def dashboard_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    user_display = st.session_state.user_name or 'Friend'
    st.markdown("<h2>Hello, " + user_display + "! 👋</h2>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.8;'>" + datetime.now().strftime('%A, %B %d, %Y') + "</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    adherence, taken, upcoming, missed = calculate_adherence()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<div style='background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; width: 150px; height: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0 auto; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);'><span style='font-size: 48px; font-weight: 800;'>" + str(adherence) + "%</span><span style='font-size: 12px;'>ADHERENCE</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.progress(adherence / 100)
    st.markdown("<h3 style='margin-top: 30px;'>📊 Today's Summary</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='text-align: center;'><div style='font-size: 42px; font-weight: 800; color: #00b894;'>" + str(taken) + "</div><p style='font-size: 12px;'>TAKEN</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='text-align: center;'><div style='font-size: 42px; font-weight: 800; color: #fdcb6e;'>" + str(upcoming) + "</div><p style='font-size: 12px;'>UPCOMING</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='text-align: center;'><div style='font-size: 42px; font-weight: 800; color: #ff7675;'>" + str(missed) + "</div><p style='font-size: 12px;'>MISSED</p></div>", unsafe_allow_html=True)
    quote = random.choice(QUOTES)
    st.markdown("<div class='quote-card'>" + '"' + quote + '"' + "</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def add_medicine_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>➕ Add Medicine</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    med_name = st.text_input("Medicine Name", placeholder="e.g., Aspirin")
    med_time = st.time_input("Time", value=time(9, 0))
    med_frequency = st.selectbox("Frequency", ["Daily", "Twice Daily", "Three Times Daily"])
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("ADD MEDICINE"):
            if med_name.strip():
                new_med = {'id': int(datetime.now().timestamp() * 1000), 'name': med_name.strip(), 'time': med_time.strftime('%H:%M'), 'frequency': med_frequency}
                st.session_state.medicines.append(new_med)
                st.session_state.medicine_status[new_med['id']] = {'taken': False, 'date': datetime.now().strftime('%Y-%m-%d')}
                st.success("Medicine added! 💊")
                st.session_state.current_screen = 'medicines'
                st.rerun()
            else:
                st.error("Please enter medicine name!")
    with col2:
        if st.button("CANCEL"):
            st.session_state.current_screen = 'medicines'
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def medicines_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📋 My Medicines</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    if not st.session_state.medicines:
        st.markdown("<div style='text-align: center; padding: 40px;'><div style='font-size: 100px; opacity: 0.5;'>💊</div><p style='opacity: 0.7;'>No medicines added yet.<br>Click 'Add New Medicine' below!</p></div>", unsafe_allow_html=True)
    else:
        for idx, med in enumerate(st.session_state.medicines):
            status_class, status_text, badge_class = get_medicine_status(med['id'], med['time'])
            st.markdown("<div class='medicine-item medicine-" + status_class + "'>", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("<h3 style='margin: 0; font-size: 20px;'>" + med['name'] + "</h3>", unsafe_allow_html=True)
                st.markdown("<p style='opacity: 0.8; font-size: 14px; margin: 5px 0;'>⏰ " + med['time'] + " • " + med['frequency'] + "</p>", unsafe_allow_html=True)
            with col2:
                st.markdown("<span class='" + badge_class + "'>" + status_text + "</span>", unsafe_allow_html=True)
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                status = st.session_state.medicine_status.get(med['id'], {})
                is_today = status.get('date') == datetime.now().strftime('%Y-%m-%d')
                if not status.get('taken', False) or not is_today:
                    if st.button("✓ Taken", key="taken_" + str(idx)):
                        st.session_state.medicine_status[med['id']] = {'taken': True, 'date': datetime.now().strftime('%Y-%m-%d')}
                        st.rerun()
            with btn_col2:
                if st.button("✏️ Edit", key="edit_" + str(idx)):
                    st.info("To edit: Delete and re-add")
            with btn_col3:
                if st.button("🗑️", key="delete_" + str(idx)):
                    st.session_state.medicines = [m for m in st.session_state.medicines if m['id'] != med['id']]
                    if med['id'] in st.session_state.medicine_status:
                        del st.session_state.medicine_status[med['id']]
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ ADD NEW MEDICINE"):
        st.session_state.current_screen = 'add_medicine'
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def rewards_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🎉 Rewards</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    adherence, _, _, _ = calculate_adherence()
    emoji = "🏆" if adherence >= 90 else "😊" if adherence >= 70 else "🙂" if adherence >= 50 else "🐢"
    title = "Champion!" if adherence >= 90 else "Great Job!" if adherence >= 70 else "Good Start!" if adherence >= 50 else "Keep Going!"
    st.markdown("<div style='text-align: center; padding: 40px;'><div style='font-size: 140px;'>" + emoji + "</div><h2 style='color: #00b894; font-size: 32px;'>" + title + "</h2><p style='font-size: 22px; font-weight: 700; margin: 15px 0;'>Adherence: " + str(adherence) + "%</p></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def settings_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>⚙️ Settings</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    st.markdown("<h3>🌙 Dark Mode</h3>", unsafe_allow_html=True)
    st.checkbox("Enabled by default", value=True)
    st.markdown("<h3 style='margin-top: 30px;'>🔔 Notifications</h3>", unsafe_allow_html=True)
    st.checkbox("Enable Notifications", value=True)
    st.markdown("<hr style='margin: 40px 0; border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    if st.button("🗑️ RESET ALL DATA"):
        if st.session_state.confirm_reset:
            st.session_state.user_name = None
            st.session_state.medicines = []
            st.session_state.medicine_status = {}
            st.session_state.current_screen = 'welcome'
            st.session_state.confirm_reset = False
            st.rerun()
        else:
            st.session_state.confirm_reset = True
            st.warning("⚠️ Click again to confirm!")
    st.markdown("</div>", unsafe_allow_html=True)

def about_screen():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>ℹ️ About</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
    st.markdown("<h3>💊 MedTimer v1.0</h3><p style='line-height: 1.8;'>Track your medication schedule and improve adherence.</p>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 30px;'>📖 How to Use</h3><ul style='line-height: 2;'><li>Add medicines</li><li>Mark as taken daily</li><li>Check adherence score</li><li>Earn rewards</li></ul>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 30px;'>⚕️ Disclaimer</h3><p style='opacity: 0.7; font-size: 14px;'>For tracking only. Consult your healthcare provider for medical advice.</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 30px 0; border-color: rgba(255,255,255,0.3);'><p style='text-align: center; opacity: 0.6;'>Made with ❤️ for better health<br>© 2025 MedTimer</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.markdown("<h1 style='text-align: center; font-size: 28px;'>💊 MedTimer</h1><hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_screen = 'dashboard'
            st.rerun()
        if st.button("💊 Medicines", use_container_width=True):
            st.session_state.current_screen = 'medicines'
            st.rerun()
        if st.button("🏆 Rewards", use_container_width=True):
            st.session_state.current_screen = 'rewards'
            st.rerun()
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_screen = 'settings'
            st.rerun()
        if st.button("ℹ️ About", use_container_width=True):
            st.session_state.current_screen = 'about'
            st.rerun()
    
    screen = st.session_state.current_screen
    if screen == 'welcome':
        welcome_screen()
    elif screen == 'setup':
        setup_screen()
    elif screen == 'dashboard':
        dashboard_screen()
    elif screen == 'add_medicine':
        add_medicine_screen()
    elif screen == 'medicines':
        medicines_screen()
    elif screen == 'rewards':
        rewards_screen()
    elif screen == 'settings':
        settings_screen()
    elif screen == 'about':
        about_screen()

if __name__ == "__main__":
    main()
    