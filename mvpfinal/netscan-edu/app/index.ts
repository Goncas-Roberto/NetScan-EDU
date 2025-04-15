import { AppRegistry } from 'react-native';
import { registerRootComponent } from 'expo';
import App from './teste.tsx';
import { name as appName } from './app.json';

// Registar a App para o Android-SDK (Android-Studio)
AppRegistry.registerComponent('netscan_edu', () => App);

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(App);
