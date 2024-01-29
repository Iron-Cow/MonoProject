import React, {useState} from "react";
import {Form} from "react-router-dom";

export default function LoginForm() {
    const [loginData, setLoginData] = useState({tg_id: '', password: ''});

    const handleChange = (e) => {
        setLoginData({...loginData, [e.target.name]: e.target.value});
    };

    return <div className="login-container">
        <Form method="post" className="login-form">
            <label htmlFor="tg_id">Login:</label>
            <input
                type="text"
                id="tg_id"
                name="tg_id"
                value={loginData.login}
                onChange={handleChange}
                required
            />

            <label htmlFor="password">Password:</label>
            <input
                type="password"
                id="password"
                name="password"
                value={loginData.password}
                onChange={handleChange}
                required
            />

            <button type="submit">Submit</button>
        </Form>
    </div>
}
