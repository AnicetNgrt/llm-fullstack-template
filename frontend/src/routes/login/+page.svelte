<script>
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { env } from '$env/dynamic/public';
	import { setAccessToken } from '$lib/accessToken';
	import { Label, Input, Heading, P } from 'flowbite-svelte';
	import ConfirmStepButton from '$components/primitive/ConfirmStepButton.svelte';
	import { writable } from 'svelte/store';
	import { Register } from "flowbite-svelte-blocks";
	import TypoLogo from '$components/primitive/TypoLogo.svelte';
	import CenterFullscreen from '$components/primitive/CenterFullscreen.svelte';
	import HoveringPanel from '$components/primitive/HoveringPanel.svelte';

	let email = '';
	let password = '';
	let error = writable(null);
	let callback = decodeURIComponent($page.url.searchParams.get('callback') ?? '');

	async function handleLogin() {
		const response = await fetch(`${env.PUBLIC_API_URL}/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ email, password })
		});

		if (response.ok) {
			const data = await response.json();

			setAccessToken(data.token);

			if (data.first_time_user) {
				goto('/onboarding' + (callback ? `?callback=${encodeURIComponent(callback)}` : ''));
			} else if (callback !== '') {
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
					<h3 class="p-0 text-xl font-medium text-gray-900 dark:text-white">Login</h3>
					{#if $error}
						<P class="text-sm font-bold mt-3 text-red-500">Error {$error.code} - {$error.message}</P>
					{/if}
					<Label class="space-y-2">
						<span>Your email</span>
						<Input type="email" name="email" placeholder="name@company.com" required bind:value={email} />
					</Label>
					<Label class="space-y-2">
						<span>Your password</span>
						<Input type="password" name="password" placeholder="•••••" required bind:value={password} />
					</Label>
					<!-- <div class="flex items-start">
						<Checkbox>Remember me</Checkbox>
						<a href="/" class="ml-auto text-sm text-blue-700 hover:underline dark:text-blue-500"
							>Forgot password?</a
						>
					</div> -->
					<ConfirmStepButton onClick={handleLogin}>
						Login
					</ConfirmStepButton>

					<p class="text-sm font-light text-gray-500 dark:text-gray-400">
						Not a client yet? <a
							href="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
							class="font-medium text-primary-600 hover:underline dark:text-primary-500">Contact us</a
						>
					</p>
				</div>
			</div>
		</Register>
	</HoveringPanel>
</CenterFullscreen>