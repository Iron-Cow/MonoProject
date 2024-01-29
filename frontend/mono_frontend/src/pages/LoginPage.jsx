import React from "react";
import {json, redirect} from "react-router-dom";
import PopUpManager from "../components/PopUpManager";
import {BACKEND_URL} from "../config/envs";
import LoginForm from "../components/LoginForm";

export default function LoginPage() {
    return <LoginForm/>
}

export async function action({request}) {
    const data = await request.formData();
    const authData = {
        tg_id: data.get('tg_id'),
        password: data.get('password'),
    };

    const endpoint = `${BACKEND_URL}/account/token/`;
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(authData),
    });

    const respData = await response.json();

    if (!response.ok) {
        let message = respData.detail || "Not valid credentials to login"
        PopUpManager.addPopUp(message);
        return json({message: message}, {status: response.status})
    }
    const token = respData.access;
    const refresh = respData.refresh;
    //
    localStorage.setItem('token', token);
    localStorage.setItem('refresh', refresh);

    return redirect('/');
}
