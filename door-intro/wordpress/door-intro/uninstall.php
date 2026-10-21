<?php
// Removes Door Intro settings when the plugin is deleted from the Plugins screen.
if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
	exit;
}
delete_option( 'door_intro_options' );
