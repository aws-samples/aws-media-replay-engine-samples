/*
 *
 *  * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *  * SPDX-License-Identifier: MIT-0
 *
 */

import React, {useState} from "react";

import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Backdrop from '@material-ui/core/Backdrop';
import CircularProgress from '@material-ui/core/CircularProgress';
import {makeStyles} from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    form: {
        width: '100%', // Fix IE 11 issue.
        marginTop: theme.spacing(1),
    },
    submit: {
        margin: theme.spacing(3, 0, 2),
    },
    backdrop: {
        zIndex: theme.zIndex.drawer + 1,
        color: '#fff',
    },
}));

function LoginForm(props) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const classes = useStyles();

    const validateForm = () => {
        return username.length > 0 && password.length > 0;
    };

    const handleUserNameChange = (e) => setUsername(e.target.value);
    const handlePasswordChange = (e) => setPassword(e.target.value);

    const handleSubmit = event => {
        event.preventDefault();

        const {onSubmit} = props;
        onSubmit(username, password);
    };

    return (
        <form className={classes.form} onSubmit={handleSubmit}>
            <TextField
                variant="outlined"
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                value={username}
                onChange={handleUserNameChange}
                autoFocus
                color="secondary"
            />
            <TextField
                variant="outlined"
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={handlePasswordChange}
                color="secondary"
            />
            {/*@todo implement remember me*/}
            {/*<FormControlLabel*/}
            {/*    control={<Checkbox value="remember" color="primary"/>}*/}
            {/*    label="Remember me"*/}
            {/*/>*/}
            <Button
                type="submit"
                fullWidth
                variant="contained"
                color="primary"
                className={classes.submit}
                disabled={!validateForm()}
            >
                Sign In
            </Button>
            {/*@todo implement forgot password and sign up*/}
            {/*Button<Grid container>*/}
            {/*    <Grid item xs>*/}
            {/*        <Link href="#" variant="body2">*/}
            {/*            Forgot password?*/}
            {/*        </Link>*/}
            {/*    </Grid>*/}
            {/*    <Grid item>*/}
            {/*        <Link href="#" variant="body2">*/}
            {/*            {"Don't have an account? Sign Up"}*/}
            {/*        </Link>*/}
            {/*    </Grid>*/}
            {/*</Grid>*/}
            {props.isLoading &&
            <Backdrop className={classes.backdrop} open={true}>
                <CircularProgress color="inherit"/>
            </Backdrop>
            }
        </form>
    );
}

export default LoginForm;