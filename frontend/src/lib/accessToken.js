import { writable } from "svelte/store";
import { page } from "$app/stores";
import useMounted from "./mounted";

export function useAccessToken() {
    let mounted = useMounted();
    let accessToken = writable(null);
    let page_url = '';

    page.subscribe((value) => {
        page_url = value.url.toString();
    });
    
    mounted.subscribe(async (value) => {
        if (!value) return;

        const token = localStorage.getItem('accessToken');
        
        if (token == null) {
            goto('/login' + (callback ? '?callback=' + encodeURIComponent(page_url) : ''));
        } else {
            accessToken.set(token);
        }
    });
    
    return accessToken;
}

export function setAccessToken(token) {
    localStorage.setItem('accessToken', token);
}

export function removeAccessToken() {
    localStorage.removeItem('accessToken');
}