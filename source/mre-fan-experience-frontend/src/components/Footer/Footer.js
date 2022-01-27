/*
 *
 *  * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *  * SPDX-License-Identifier: MIT-0
 *
 */

import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Copyright from '../../common/Copyright';
import Grid from "@material-ui/core/Grid";

import LIGHT_TEAM_LOGO from "../../assets/light-bdsi-logo.svg";
import DARK_TEAM_LOGO from "../../assets/dark-bdsi-logo.svg";

const useStyles = makeStyles((theme) => ({
    footer: {
        padding: theme.spacing(2, 1),
        marginTop: 'auto',
        color: theme.palette.primary.contrastText,
        backgroundColor: theme.palette.primary.main
    },
    media: {
        height: 25
    },
}));

function Footer() {
    const classes = useStyles();

    return (
        <footer className={classes.footer}>
            <Grid container direction="row" justify="space-between" alignItems="center">
                <Grid item>
                    <Copyright/>
                </Grid>
                <Grid item>
                    <img className={classes.media} alt="team-logo"
                         src={DARK_TEAM_LOGO}/>
                </Grid>
            </Grid>
        </footer>
    );
}

export default Footer;