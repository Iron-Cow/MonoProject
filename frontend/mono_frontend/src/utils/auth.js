import {redirect} from 'react-router-dom';
import PopUpManager from "../components/PopUpManager";


export async function getAuthToken() {
    const refresh = localStorage.getItem('refresh');

    const token = await refreshAuthToken(refresh)
    console.log("if token -> ", token, "aaa")
    if (!token) {
        return null;
    }
    return token;


}

async function refreshAuthToken(refresh) {
    const endpoint = 'http://localhost:8000/account/token-refresh/';
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({refresh: refresh}),
    });
    const data = await response.json();

    if (!response.ok) {
        PopUpManager.addPopUp(data.detail);
        return null
    }
    return data.access

}

export async function checkAuthLoader() {
    const token = await getAuthToken();
    console.log("checkAuthLoader", token)
    if (!token) {
        return redirect('/login');
    }
    return token
}
