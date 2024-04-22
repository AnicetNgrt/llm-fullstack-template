import { onMount } from "svelte";
import { goto } from '$app/navigation';
import { writable } from "svelte/store";

export default function useMounted() {
    let mounted = writable(false);
    
    onMount(() => {
        mounted.set(true);
    });
    
    return mounted;
}