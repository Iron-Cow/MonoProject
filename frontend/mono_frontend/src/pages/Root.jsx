import PopUpManager from "../components/PopUpManager";
import {Outlet} from "react-router-dom";

export default function Root() {

    return <>
        <PopUpManager></PopUpManager>
        <Outlet/>
    </>
}
