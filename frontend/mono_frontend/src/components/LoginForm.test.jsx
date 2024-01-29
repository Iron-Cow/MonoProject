import React from 'react';
import {render, screen} from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginForm from "../components/LoginForm";
import {MemoryRouter} from "react-router-dom";

// // Mocking localStorage
// const localStorageMock = (function () {
//     let store = {};
//     return {
//         getItem: function (key) {
//             return store[key] || null;
//         },
//         setItem: function (key, value) {
//             store[key] = value.toString();
//         },
//         clear: function () {
//             store = {};
//         }
//     };
// })();
//
// Object.defineProperty(window, 'localStorage', {
//     value: localStorageMock
// });
//
// // Mocking fetch
// global.fetch = jest.fn(() =>
//     Promise.resolve({
//         ok: true,
//         json: () => Promise.resolve({access: 'testToken', refresh: 'testRefresh'}),
//     })
// );

describe('LoginForm', () => {
    // beforeEach(() => {
    //     fetch.mockClear();
    //     window.localStorage.clear();
    // });

    it('renders the form with all fields and a submit button', () => {
        render(
            <MemoryRouter>
                <LoginForm/>
            </MemoryRouter>
        );
        expect(screen.getByLabelText(/login:/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/password:/i)).toBeInTheDocument();
        expect(screen.getByRole('button', {name: /submit/i})).toBeInTheDocument();
    })


    // it('updates state on input change', () => {
    //     render(
    //         <MemoryRouter>
    //             <LoginPage/>
    //         </MemoryRouter>
    //     );
    //     ;
    //
    //     const loginInput = screen.getByLabelText(/login:/i);
    //     const passwordInput = screen.getByLabelText(/password:/i);
    //
    //     fireEvent.change(loginInput, {target: {value: 'testuser'}});
    //     fireEvent.change(passwordInput, {target: {value: 'password123'}});
    //
    //     expect(loginInput.value).toBe('testuser');
    //     expect(passwordInput.value).toBe('password123');
    // });

    // it('submits the form with the correct data', async () => {
    //     render(<LoginPage/>);
    //
    //     const loginInput = screen.getByLabelText(/login:/i);
    //     const passwordInput = screen.getByLabelText(/password:/i);
    //     const submitButton = screen.getByRole('button', {name: /submit/i});
    //
    //     fireEvent.change(loginInput, {target: {value: 'testuser'}});
    //     fireEvent.change(passwordInput, {target: {value: 'password123'}});
    //
    //     fireEvent.click(submitButton);
    //
    //     await waitFor(() => {
    //         expect(fetch).toHaveBeenCalledTimes(1);
    //         expect(fetch).toHaveBeenCalledWith(expect.any(String), {
    //             method: 'POST',
    //             headers: {'Content-Type': 'application/json'},
    //             body: JSON.stringify({tg_id: 'testuser', password: 'password123'}),
    //         });
    //     });
    // })
})
