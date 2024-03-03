import {redirect} from 'react-router-dom';

export default function Logout() {
    return action()
}

export function action() {
    console.log("logging out...")
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
    return redirect('/login');
}
