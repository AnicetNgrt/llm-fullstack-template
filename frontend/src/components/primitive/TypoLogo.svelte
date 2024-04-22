<script>
    import { Heading } from 'flowbite-svelte';

    let classes;
    export { classes as class };
    export let size = "medium";
</script>

{#if size == "large"}
<Heading tag="h1" class={classes} customSize="text-3xl font-extrabold  md:text-4xl lg:text-5xl">
    YOUR APP
</Heading>
{/if}
{#if size == "medium"}
<Heading tag="h2" class={classes} customSize="text-2xl font-extrabold  md:text-3xl lg:text-4xl">
    YOUR APP
</Heading>
{/if}
{#if size == "small"}
<Heading tag="h3" class={classes} customSize="text-1xl font-extrabold  md:text-2xl lg:text-3xl">
    YOUR APP
</Heading>
{/if}