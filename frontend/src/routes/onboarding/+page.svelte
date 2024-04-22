<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { env } from '$env/dynamic/public';
	import { useAccessToken } from '$lib/accessToken';
	import { Label, Input, P } from 'flowbite-svelte';
	import ConfirmStepButton from '$components/primitive/ConfirmStepButton.svelte';
	import { writable } from 'svelte/store';
	import { Register } from "flowbite-svelte-blocks";
	import TypoLogo from '$components/primitive/TypoLogo.svelte';
	import CenterFullscreen from '$components/primitive/CenterFullscreen.svelte';
	import HoveringPanel from '$components/primitive/HoveringPanel.svelte';


	let username = '';
	let password = '';
	let passwordRepeat = '';
	let error = writable(null);
	let callback = decodeURIComponent($page.url.searchParams.get('callback') ?? '');
	let accessToken = useAccessToken($page.url.toString());

	async function handleOnboarding() {
		if (password !== passwordRepeat) {
			error.set({ code: 400, message: 'Passwords do not match' });
			passwordRepeat = '';
			password = '';
			return;
		}
		
		const response = await fetch(`${env.PUBLIC_API_URL}/user/onboarding?token=${$accessToken}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username, password })
		});

		if (response.ok) {
			if (callback !== '') {
				goto(callback);
			} else {
				goto('/app?id=new');
			}
		} else {
			const errorData = await response.json();
			const errorCode = response.status;
			error.set({ code: errorCode, message: errorData.error });
		}
	}
</script>


<CenterFullscreen>
	<HoveringPanel>
		<Register href="/">
			<svelte:fragment slot="top">
				<TypoLogo size="medium" class="mb-6" />
			</svelte:fragment>
			<div class="space-y-4 p-6 sm:p-8 md:space-y-6">
				<div class="flex flex-col space-y-6">
					<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">
						Onboarding
					</h3>
					{#if $error}
						<P class="text-sm font-bold mt-3 text-red-500">Error {$error.code} - {$error.message}</P>
					{/if}
					<Label class="space-y-2">
						<span>Choose a username</span>
						<Input type="text" name="text" placeholder="username" required bind:value={username} />
					</Label>
					<Label class="space-y-2">
						<span>Choose a password</span>
						<Input type="password" name="password" placeholder="•••••" required bind:value={password} />
					</Label>
					<Label class="space-y-2">
						<span>Repeat password</span>
						<Input type="password" name="password" placeholder="•••••" required bind:value={passwordRepeat} />
					</Label>
					<ConfirmStepButton onClick={handleOnboarding}>
						Confirm
					</ConfirmStepButton>
				</div>
			</div>
		</Register>
	</HoveringPanel>
</CenterFullscreen>
