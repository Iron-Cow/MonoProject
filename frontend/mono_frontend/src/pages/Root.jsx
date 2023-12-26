import PopUpManager from "../components/PopUpManager";
import {Outlet} from "react-router-dom";

export default function Root() {
    const apiUrl = process.env.REACT_APP_API_URL
    console.log(process.env)
    console.log(apiUrl)
    console.log(process.env.NODE_ENV)
    return <>
        <h1>ENV7 {process.env.REACT_APP_DB_NAME}</h1>
        <h1>ENV4 {process.env.REACT_APP_API_HOST}</h1>
        <h1>AAA</h1>

        <PopUpManager></PopUpManager>
        <Outlet/>
    </>
}
