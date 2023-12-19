import React, {useEffect, useState} from 'react';
import PopUp from './PopUp';
import "./PopUp.css"


const POPUP_LIFE_TIME_SECONDS = 4
const PopUpManager = () => {
    const [popUps, setPopUps] = useState([]);
    const addPopUp = (message) => {
        const id = Date.now() + POPUP_LIFE_TIME_SECONDS * 1000; // Unique ID for each pop-up
        setPopUps([...popUps, {id, message}]);
    };
    useEffect(() => {
        let i = setInterval(() => {
            let now = Date.now()
            if (popUps.length) {
                setPopUps(popUps.filter(popUp => popUp.id >= now))
            }
        }, 1000)
        return () => clearInterval(i)
    }, [popUps]);

    PopUpManager.addPopUp = addPopUp;
    return (
        <div className="pop-up-manager">
            {popUps.map(popUp => (
                <PopUp
                    key={popUp.id}
                    id={popUp.id}
                    message={popUp.message}/>
            ))}
        </div>
    );

};

export default PopUpManager;
