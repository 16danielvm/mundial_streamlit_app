import streamlit as st

from auth import change_password


def tab_account(user_id, username):
    st.subheader("⚙️ Mi cuenta")

    if not user_id:
        st.warning("Primero inicia sesión para administrar tu cuenta.")
        return

    st.markdown("### Seguridad")
    st.caption("Cambia tu contraseña de acceso.")

    with st.form("change_password_form"):
        current_password = st.text_input("Contraseña actual", type="password")
        new_password = st.text_input("Nueva contraseña", type="password")
        confirm_password = st.text_input("Confirmar nueva contraseña", type="password")

        submitted = st.form_submit_button("Actualizar contraseña")

    if submitted:
        ok, msg = change_password(
            user_id,
            current_password,
            new_password,
            confirm_password,
        )

        if ok:
            st.success(msg)
        else:
            st.error(msg)