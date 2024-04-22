import { goto } from '$app/navigation';
import { writable } from "svelte/store";
import { useAccessToken, removeAccessToken } from "./accessToken";
import { env } from '$env/dynamic/public';
import { UserOutline } from 'flowbite-svelte-icons';
import { page } from "$app/stores";

export async function getUserInfos(jwt) {
    const response = await fetch(`${env.PUBLIC_API_URL}/user?token=${jwt}`, {
        method: 'GET'
    });

    if (response.ok) {
        const data = await response.json();
        return data;
    } else {
        return null;
    }
}

export default function useUserInfos() {
    let userInfos = writable(null);

    let accessToken = useAccessToken();

    let page_url = '';

    page.subscribe((value) => {
        page_url = value.url.toString();
    });

    accessToken.subscribe(async (value) => {
        if (!value) return;

        const infos = await getUserInfos(value);
		
        if (infos == null) {
			removeAccessToken();
            console.log('No user infos');
			goto('/login' + (callback ? '?callback=' + encodeURIComponent(page_url) : ''));
		} else {
            userInfos.set(infos);
        }
    });

    return userInfos;
}