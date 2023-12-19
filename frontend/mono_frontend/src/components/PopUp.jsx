import React from 'react';

const PopUp = ({message, id}) => {

    return (
        <div className="pop-up">
            {message} - {id}
        </div>
    );
}
export default PopUp;
