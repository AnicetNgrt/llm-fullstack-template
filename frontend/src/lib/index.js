import { env } from '$env/dynamic/public';


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